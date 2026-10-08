# Keys NG M1.20.4 — Manuale completo per la revisione del codice

Versione: `0.1.20.dev4`. Questo documento è generato dall'esatto albero sorgente Python distribuito con M1.20.4.

## Scopo e metodo di lettura

Questo manuale è una mappa orientata al revisore, non sostituisce la lettura del sorgente. Documenta ogni classe e funzione Python (inclusi gli helper annidati) con firma, intervallo di righe, chiamate dirette, eccezioni esplicite, scritture di stato, forma del flusso di controllo ed effetti rilevanti per la sicurezza. I marker stabili `symbol:` sono verificati automaticamente dai test, così nessun simbolo eseguibile non documentato può entrare silenziosamente nella release.

## Architettura e confini di fiducia

- `models` contiene gli oggetti di dominio plaintext validati. Il plaintext esiste nella memoria Python solo quando necessario.
- `storage.vault` è il confine centrale di policy. Cifra prima della persistenza, verifica le firme dopo la decifratura, collega i record al catalogo firmato e svuota le cache di metadati decifrati al lock.
- `crypto` delega la passphrase della chiave privata a GnuPG/gpg-agent/pinentry; Keys NG non richiede mai tale passphrase.
- I dati persistenti delle credenziali sono ciphertext OpenPGP per-record. Anche `catalog.gpg` e `folders.gpg` sono cifrati e firmati. `vault.json` è intenzionalmente metadata di policy in chiaro e non deve contenere credenziali.
- Le azioni esterne sono basate su argv e usano `shell=False`. Le opzioni SSH avanzate restano un confine di fiducia del record perché OpenSSH stesso può eseguire comandi tramite opzioni come ProxyCommand/LocalCommand.
- Il catalogo cifrato rileva sostituzione/rollback di un singolo record tramite SHA-256 del ciphertext più revisione. Il rollback coordinato di record e catalogo resta un rischio residuo documentato.

## Flussi di esecuzione principali

```text
CLI/TUI/GUI -> Vault -> CryptoBackend -> GnuPG -> gpg-agent/pinentry
                    |
                    +-> records/<uuid>.gpg
                    +-> catalog.gpg
                    +-> folders.gpg
public-key contributor -> inbox/<random>.gpg -> explicit import -> Vault.save_entry()
```

## Riferimento esaustivo modulo per modulo

### `keys_ng.__main__`

Modulo sorgente.

**Sorgente:** `src/keys_ng/__main__.py`  
**Simboli eseguibili:** 0

**Dipendenze dirette del modulo:** `keys_ng.gui.main`

### `keys_ng.cli.main`

Parser e dispatcher della riga di comando per tutti i flussi CLI.

**Sorgente:** `src/keys_ng/cli/main.py`  
**Simboli eseguibili:** 7

**Dipendenze dirette del modulo:** `__future__`, `argparse`, `getpass`, `keys_ng`, `keys_ng.crypto.factory`, `keys_ng.crypto.gpg_process`, `keys_ng.errors`, `keys_ng.i18n`, `keys_ng.migration.keepassxc`, `keys_ng.migration.keepassxc_export`, `keys_ng.migration.migrator`, `keys_ng.models`, `keys_ng.platform.desktop_integration`, `keys_ng.services.actions`, `keys_ng.services.clipboard`, `keys_ng.services.diagnostics`, `keys_ng.services.doctor`, `keys_ng.services.passwords`, `keys_ng.services.qr`, `keys_ng.services.ssh_options`, `keys_ng.services.totp`, `keys_ng.services.trusted_signers`, `keys_ng.services.vault_init`, `keys_ng.storage.inbox`, `keys_ng.storage.settings`, `keys_ng.storage.vault`, `os`, `pathlib`, `sys`, `tempfile`, `time`

<!-- symbol:keys_ng.cli.main:_settings -->
#### `_settings`

**Tipo:** funzione/metodo  
**Righe:** 40-41  
**Firma:** `def _settings() -> AppSettings`  
**Scopo:** Helper interno che implementa `_settings`.

**Chiamate dirette osservate nel corpo:** `AppSettings.load`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.cli.main:_crypto -->
#### `_crypto`

**Tipo:** funzione/metodo  
**Righe:** 44-46  
**Firma:** `def _crypto()`  
**Scopo:** Helper interno che implementa `_crypto`.

**Chiamate dirette osservate nel corpo:** `_settings`, `create_crypto_backend`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.cli.main:_vault -->
#### `_vault`

**Tipo:** funzione/metodo  
**Righe:** 49-50  
**Firma:** `def _vault(path: str) -> Vault`  
**Scopo:** Helper interno che implementa `_vault`.

**Chiamate dirette osservate nel corpo:** `Vault`, `_crypto`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.cli.main:_print_items -->
#### `_print_items`

**Tipo:** funzione/metodo  
**Righe:** 53-56  
**Firma:** `def _print_items(items) -> None`  
**Scopo:** Helper interno che implementa `_print_items`.

**Chiamate dirette osservate nel corpo:** `join`, `print`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.cli.main:build_parser -->
#### `build_parser`

**Tipo:** funzione/metodo  
**Righe:** 59-238  
**Firma:** `def build_parser() -> argparse.ArgumentParser`  
**Scopo:** Costruisce `build_parser`.

**Chiamate dirette osservate nel corpo:** `action.add_argument`, `add.add_argument`, `argparse.ArgumentParser`, `delete.add_argument`, `deposit.add_argument`, `desktop.add_subparsers`, `desktop_sub.add_parser`, `edit.add_argument`, `export_entry.add_argument`, `export_vault.add_argument`, `folder.add_subparsers`, `folder_create.add_argument`, `folder_delete.add_argument`, `folder_list.add_argument`, `folder_move.add_argument`, `folder_rename.add_argument`, `folder_sub.add_parser`, `gen.add_argument`, `health.add_argument`, `inbox.add_argument`, `init.add_argument`, `keys.add_argument`, `kp.add_argument`, `lock.add_argument`, `ls.add_argument`, `migrate.add_argument`, `move.add_argument`, `otp.add_argument`, `p.add_argument`, `p.add_subparsers`, `password.add_argument`, `reindex.add_argument`, `search.add_argument`, `show.add_argument`, `sub.add_parser`, `trust.add_subparsers`, `trust_add.add_argument`, `trust_list.add_argument`, `trust_remove.add_argument`, `trust_sub.add_parser`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.cli.main:run -->
#### `run`

**Tipo:** funzione/metodo  
**Righe:** 241-530  
**Firma:** `def run(args: argparse.Namespace) -> int`  
**Scopo:** Implementa l'operazione `run` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Action`, `Entry.create`, `GPGProcessBackend`, `KeysNGError`, `Path`, `Vault`, `VaultInitRequest`, `_`, `_crypto`, `_print_items`, `_settings`, `actions.append`, `add_trusted_signer`, `args.folder.strip`, `args.parent.strip`, `collect_doctor_checks`, `copy_secret_cli`, `create_vault`, `crypto.hard_lock`, `crypto.list_keys`, `deposit_crypto.import_public_key`, `deposit_crypto.resolve_fingerprint`, `desktop_integration_status`, `dict.fromkeys`, `entry.actions.insert`, `expanduser`, `export_entry_xml`, `export_vault_xml`, `flags.append`, `format`, `generate_password`, `generate_totp`, `getpass`, `import_inbox`, `import_keepassxc`, `imported.extend`, `input`, `install_user_desktop_integration`, `join`, `launch_action`, `len`, `list`, `list_trusted_signers`, `migrate_legacy_tree`, `next`, `os.chmod`, `parse_otpauth_uri`, `parse_ssh_options`, `parse_totp_qr_file`, `print`, `read_bytes`, `remove_trusted_signer`, `strip`, `tempfile.TemporaryDirectory`, `temporary_home.cleanup`, `time.sleep`, `totp.append`, `tuple`, `uninstall_user_desktop_integration`, `vault.catalog_health`, `vault.create_folder_path`, `vault.delete_entry`, `vault.delete_folder`, `vault.folder_path`, `vault.get_entry`, `vault.list_folders`, `vault.list_items`, `vault.move_entry`, `vault.move_folder`, `vault.reindex`, `vault.rename_folder`, `vault.resolve_folder_path`, `vault.resolved_action`, `vault.resolved_password`, `vault.save_entry`, `vault.search`, `write_encrypted_entry`, `write_export`.

**Eccezioni sollevate esplicitamente:** `KeysNGError`.

**Attributi oggetto modificati:** `action.username`, `entry.actions`, `entry.folder_id`, `entry.revision`, `entry.title`, `entry.usernames`, `ssh_action.ssh_options`, `ssh_action.ssh_x11_forwarding`.

**Forma del flusso di controllo:** 79 blocchi condizionali, 11 cicli, 3 blocchi try, 0 context manager, 22 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.cli.main:main -->
#### `main`

**Tipo:** funzione/metodo  
**Righe:** 533-544  
**Firma:** `def main() -> None`  
**Scopo:** Implementa l'operazione `main` in questo modulo.

**Chiamate dirette osservate nel corpo:** `SystemExit`, `_settings`, `build_parser`, `configure_diagnostics`, `configure_language`, `get_logger`, `info`, `parser.parse_args`, `print`, `run`.

**Eccezioni sollevate esplicitamente:** `SystemExit`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.crypto.backend`

Contratti dei backend crittografici e record immutabili per risultati e chiavi.

**Sorgente:** `src/keys_ng/crypto/backend.py`  
**Simboli eseguibili:** 11

**Dipendenze dirette del modulo:** `__future__`, `abc`, `dataclasses`

<!-- symbol:keys_ng.crypto.backend:DecryptionResult -->
#### `DecryptionResult`

**Tipo:** classe  
**Righe:** 8-12  
**Campi dichiarati:** `plaintext`, `signer_fingerprint`, `signature_valid`, `primary_signer_fingerprint`  
**Responsabilità:** Implementa l'operazione `DecryptionResult` in questo modulo.

<!-- symbol:keys_ng.crypto.backend:KeyInfo -->
#### `KeyInfo`

**Tipo:** classe  
**Righe:** 16-28  
**Campi dichiarati:** `fingerprint`, `user_ids`, `can_encrypt`, `can_sign`, `secret`, `revoked`, `expired`  
**Metodi:** `label`  
**Responsabilità:** Implementa l'operazione `KeyInfo` in questo modulo.

<!-- symbol:keys_ng.crypto.backend:KeyInfo.label -->
#### `KeyInfo.label`

**Tipo:** funzione/metodo  
**Righe:** 26-28  
**Firma:** `def label(self) -> str`  
**Scopo:** Implementa l'operazione `label` in questo modulo.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend -->
#### `CryptoBackend`

**Tipo:** classe  
**Righe:** 31-62  
**Basi:** `ABC`  
**Metodi:** `encrypt`, `decrypt`, `diagnose`, `list_keys`, `resolve_fingerprint`, `import_public_key`, `hard_lock`  
**Responsabilità:** Interfaccia astratta che isola la logica del vault dall'implementazione crittografica.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.encrypt -->
#### `CryptoBackend.encrypt`

**Tipo:** funzione/metodo  
**Righe:** 33-34  
**Firma:** `def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None=None) -> bytes`  
**Scopo:** Implementa l'operazione `encrypt` in questo modulo.

**Eccezioni sollevate esplicitamente:** `NotImplementedError`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.decrypt -->
#### `CryptoBackend.decrypt`

**Tipo:** funzione/metodo  
**Righe:** 37-38  
**Firma:** `def decrypt(self, ciphertext: bytes) -> DecryptionResult`  
**Scopo:** Implementa l'operazione `decrypt` in questo modulo.

**Eccezioni sollevate esplicitamente:** `NotImplementedError`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.diagnose -->
#### `CryptoBackend.diagnose`

**Tipo:** funzione/metodo  
**Righe:** 41-42  
**Firma:** `def diagnose(self) -> list[tuple[str, bool, str]]`  
**Scopo:** Implementa l'operazione `diagnose` in questo modulo.

**Eccezioni sollevate esplicitamente:** `NotImplementedError`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.list_keys -->
#### `CryptoBackend.list_keys`

**Tipo:** funzione/metodo  
**Righe:** 44-45  
**Firma:** `def list_keys(self, secret: bool=False) -> list[KeyInfo]`  
**Scopo:** Restituisce una vista filtrata/elencata di `list_keys`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.resolve_fingerprint -->
#### `CryptoBackend.resolve_fingerprint`

**Tipo:** funzione/metodo  
**Righe:** 47-51  
**Firma:** `def resolve_fingerprint(self, selector: str, secret: bool=False) -> str`  
**Scopo:** Risolve `resolve_fingerprint`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `k.fingerprint.upper`, `len`, `selector.upper`, `self.list_keys`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.import_public_key -->
#### `CryptoBackend.import_public_key`

**Tipo:** funzione/metodo  
**Righe:** 53-58  
**Firma:** `def import_public_key(self, key_data: bytes) -> list[str]`  
**Scopo:** Import public-key material and return available encryption fingerprints. Backends that do not support key import may raise ``NotImplementedError``.

**Chiamate dirette osservate nel corpo:** `NotImplementedError`.

**Eccezioni sollevate esplicitamente:** `NotImplementedError`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.backend:CryptoBackend.hard_lock -->
#### `CryptoBackend.hard_lock`

**Tipo:** funzione/metodo  
**Righe:** 60-62  
**Firma:** `def hard_lock(self) -> None`  
**Scopo:** Drop any cached private-key authorization if supported by the backend.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.crypto.discovery`

Rilevamento multipiattaforma degli eseguibili GnuPG, incluse le installazioni Gpg4win/GnuPG su Windows.

**Sorgente:** `src/keys_ng/crypto/discovery.py`  
**Simboli eseguibili:** 5

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `keys_ng.platform.host`, `os`, `pathlib`, `sys`

<!-- symbol:keys_ng.crypto.discovery:ExecutableDiscovery -->
#### `ExecutableDiscovery`

**Tipo:** classe  
**Righe:** 12-16  
**Campi dichiarati:** `path`, `method`  
**Responsabilità:** Resolved external executable and the method used to find it.

<!-- symbol:keys_ng.crypto.discovery:_candidate_is_executable -->
#### `_candidate_is_executable`

**Tipo:** funzione/metodo  
**Righe:** 19-28  
**Firma:** `def _candidate_is_executable(path: str | Path | None) -> str | None`  
**Scopo:** Helper interno che implementa `_candidate_is_executable`.

**Chiamate dirette osservate nel corpo:** `Path`, `candidate.is_file`, `candidate.resolve`, `expanduser`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 4 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.discovery:_windows_registry_roots -->
#### `_windows_registry_roots`

**Tipo:** funzione/metodo  
**Righe:** 31-62  
**Firma:** `def _windows_registry_roots() -> list[Path]`  
**Scopo:** Return GnuPG/Gpg4win installation roots advertised by the Windows registry.

**Chiamate dirette osservate nel corpo:** `Path`, `isinstance`, `os.path.expandvars`, `roots.append`, `value.strip`, `winreg.OpenKey`, `winreg.QueryValueEx`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 3 cicli, 3 blocchi try, 1 context manager, 3 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.discovery:_windows_standard_roots -->
#### `_windows_standard_roots`

**Tipo:** funzione/metodo  
**Righe:** 65-81  
**Firma:** `def _windows_standard_roots() -> list[Path]`  
**Scopo:** Helper interno che implementa `_windows_standard_roots`.

**Chiamate dirette osservate nel corpo:** `Path`, `casefold`, `os.environ.get`, `result.append`, `roots.extend`, `seen.add`, `set`, `str`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.discovery:discover_gnupg_executable -->
#### `discover_gnupg_executable`

**Tipo:** funzione/metodo  
**Righe:** 84-125  
**Firma:** `def discover_gnupg_executable(name: str, configured: str='') -> ExecutableDiscovery`  
**Scopo:** Resolve a GnuPG executable without a shell. Precedence is: explicit user configuration, PATH/Flatpak host PATH, Windows registry installation roots, then conventional Windows locations.

**Chiamate dirette osservate nel corpo:** `ExecutableDiscovery`, `Path`, `_candidate_is_executable`, `_windows_registry_roots`, `_windows_standard_roots`, `configured.strip`, `host_which`.

**Forma del flusso di controllo:** 9 blocchi condizionali, 4 cicli, 0 blocchi try, 0 context manager, 8 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.crypto.factory`

Seleziona il backend crittografico configurato.

**Sorgente:** `src/keys_ng/crypto/factory.py`  
**Simboli eseguibili:** 1

**Dipendenze dirette del modulo:** `__future__`, `keys_ng.crypto.backend`, `keys_ng.crypto.gpg_process`

<!-- symbol:keys_ng.crypto.factory:create_crypto_backend -->
#### `create_crypto_backend`

**Tipo:** funzione/metodo  
**Righe:** 7-36  
**Firma:** `def create_crypto_backend(preference: str='auto', gpg_executable: str='', gpgconf_executable: str='') -> CryptoBackend`  
**Scopo:** Return the requested backend. Explicit GnuPG executable overrides select the subprocess backend so the configured paths are honored consistently on every platform.

**Chiamate dirette osservate nel corpo:** `GPGMEBackend`, `GPGProcessBackend`, `RuntimeError`, `ValueError`, `gpg_executable.strip`, `gpgconf_executable.strip`, `preference.lower`.

**Eccezioni sollevate esplicitamente:** `RuntimeError`, `ValueError`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 4 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.crypto.gpg_process`

Backend GnuPG a sottoprocesso; i dati passano via pipe e non viene usata una shell.

**Sorgente:** `src/keys_ng/crypto/gpg_process.py`  
**Simboli eseguibili:** 12

**Dipendenze dirette del modulo:** `__future__`, `keys_ng.crypto.backend`, `keys_ng.crypto.discovery`, `keys_ng.errors`, `keys_ng.platform.host`, `keys_ng.services.diagnostics`, `os`, `subprocess`, `time`, `typing`

<!-- symbol:keys_ng.crypto.gpg_process:_windows_creationflags -->
#### `_windows_creationflags`

**Tipo:** funzione/metodo  
**Righe:** 18-22  
**Firma:** `def _windows_creationflags() -> int`  
**Scopo:** Suppress transient console windows for GnuPG helpers on Windows.

**Chiamate dirette osservate nel corpo:** `getattr`, `int`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend -->
#### `GPGProcessBackend`

**Tipo:** classe  
**Righe:** 25-196  
**Basi:** `CryptoBackend`  
**Metodi:** `__init__`, `_base_args`, `_run`, `encrypt`, `decrypt`, `list_keys`, `import_public_key`, `resolve_fingerprint`, `hard_lock`, `diagnose`  
**Responsabilità:** GnuPG backend using argv arrays and pipes only; never invokes a shell.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.__init__ -->
#### `GPGProcessBackend.__init__`

**Tipo:** funzione/metodo  
**Righe:** 28-44  
**Firma:** `def __init__(self, executable: str | None=None, gpgconf_executable: str | None=None, homedir: str | None=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `_LOG.debug`, `bool`, `discover_gnupg_executable`.

**Attributi oggetto modificati:** `self.executable`, `self.executable_discovery`, `self.gpgconf_discovery`, `self.gpgconf_executable`, `self.homedir`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend._base_args -->
#### `GPGProcessBackend._base_args`

**Tipo:** funzione/metodo  
**Righe:** 46-47  
**Firma:** `def _base_args(self) -> list[str]`  
**Scopo:** Helper interno che implementa `_base_args`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend._run -->
#### `GPGProcessBackend._run`

**Tipo:** funzione/metodo  
**Righe:** 49-84  
**Firma:** `def _run(self, args: Iterable[str], data: bytes=b'', *, check: bool=True) -> subprocess.CompletedProcess[bytes]`  
**Scopo:** Helper interno che implementa `_run`.

**Chiamate dirette osservate nel corpo:** `CryptoError`, `_LOG.debug`, `_LOG.exception`, `_windows_creationflags`, `elapsed_ms`, `host_argv`, `len`, `list`, `os.environ.copy`, `proc.stderr.decode`, `safe_operation_args`, `self._base_args`, `strip`, `subprocess.run`, `time.perf_counter`.

**Eccezioni sollevate esplicitamente:** `CryptoError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.encrypt -->
#### `GPGProcessBackend.encrypt`

**Tipo:** funzione/metodo  
**Righe:** 86-95  
**Firma:** `def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None=None) -> bytes`  
**Scopo:** Implementa l'operazione `encrypt` in questo modulo.

**Chiamate dirette osservate nel corpo:** `CryptoError`, `args.append`, `args.extend`, `self._run`.

**Eccezioni sollevate esplicitamente:** `CryptoError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.decrypt -->
#### `GPGProcessBackend.decrypt`

**Tipo:** funzione/metodo  
**Righe:** 97-118  
**Firma:** `def decrypt(self, ciphertext: bytes) -> DecryptionResult`  
**Scopo:** Implementa l'operazione `decrypt` in questo modulo.

**Chiamate dirette osservate nel corpo:** `DecryptionResult`, `len`, `proc.stderr.decode`, `raw_line.startswith`, `self._run`, `splitlines`, `status.split`, `status.startswith`, `upper`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.list_keys -->
#### `GPGProcessBackend.list_keys`

**Tipo:** funzione/metodo  
**Righe:** 120-148  
**Firma:** `def list_keys(self, secret: bool=False) -> list[KeyInfo]`  
**Scopo:** Restituisce una vista filtrata/elencata di `list_keys`.

**Chiamate dirette osservate nel corpo:** `KeyInfo`, `caps.lower`, `current.get`, `keys.append`, `len`, `line.split`, `proc.stdout.decode`, `self._run`, `splitlines`, `upper`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.import_public_key -->
#### `GPGProcessBackend.import_public_key`

**Tipo:** funzione/metodo  
**Righe:** 150-152  
**Firma:** `def import_public_key(self, key_data: bytes) -> list[str]`  
**Scopo:** Importa `import_public_key`.

**Chiamate dirette osservate nel corpo:** `self._run`, `self.list_keys`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.resolve_fingerprint -->
#### `GPGProcessBackend.resolve_fingerprint`

**Tipo:** funzione/metodo  
**Righe:** 154-161  
**Firma:** `def resolve_fingerprint(self, selector: str, secret: bool=False) -> str`  
**Scopo:** Risolve `resolve_fingerprint`.

**Chiamate dirette osservate nel corpo:** `CryptoError`, `any`, `len`, `selector.strip`, `self.list_keys`, `upper`.

**Eccezioni sollevate esplicitamente:** `CryptoError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.hard_lock -->
#### `GPGProcessBackend.hard_lock`

**Tipo:** funzione/metodo  
**Righe:** 163-178  
**Firma:** `def hard_lock(self) -> None`  
**Scopo:** Implementa l'operazione `hard_lock` in questo modulo.

**Chiamate dirette osservate nel corpo:** `CryptoError`, `_windows_creationflags`, `host_argv`, `proc.stderr.decode`, `strip`, `subprocess.run`.

**Eccezioni sollevate esplicitamente:** `CryptoError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.crypto.gpg_process:GPGProcessBackend.diagnose -->
#### `GPGProcessBackend.diagnose`

**Tipo:** funzione/metodo  
**Righe:** 180-196  
**Firma:** `def diagnose(self) -> list[tuple[str, bool, str]]`  
**Scopo:** Implementa l'operazione `diagnose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `bool`, `checks.append`, `len`, `proc.stdout.decode`, `self._run`, `self.list_keys`, `splitlines`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.crypto.gpgme_backend`

Modulo riservato a un futuro backend GPGME; attualmente non contiene simboli eseguibili.

**Sorgente:** `src/keys_ng/crypto/gpgme_backend.py`  
**Simboli eseguibili:** 0

**Dipendenze dirette del modulo:** `__future__`

### `keys_ng.errors`

Gerarchia delle eccezioni del progetto.

**Sorgente:** `src/keys_ng/errors.py`  
**Simboli eseguibili:** 6

<!-- symbol:keys_ng.errors:KeysNGError -->
#### `KeysNGError`

**Tipo:** classe  
**Righe:** 1-2  
**Basi:** `Exception`  
**Responsabilità:** Base application error.

<!-- symbol:keys_ng.errors:CryptoError -->
#### `CryptoError`

**Tipo:** classe  
**Righe:** 5-6  
**Basi:** `KeysNGError`  
**Responsabilità:** OpenPGP operation failed.

<!-- symbol:keys_ng.errors:SignatureError -->
#### `SignatureError`

**Tipo:** classe  
**Righe:** 9-10  
**Basi:** `CryptoError`  
**Responsabilità:** A required signature was missing or invalid.

<!-- symbol:keys_ng.errors:VaultError -->
#### `VaultError`

**Tipo:** classe  
**Righe:** 13-14  
**Basi:** `KeysNGError`  
**Responsabilità:** Vault storage or configuration error.

<!-- symbol:keys_ng.errors:LegacyFormatError -->
#### `LegacyFormatError`

**Tipo:** classe  
**Righe:** 17-18  
**Basi:** `KeysNGError`  
**Responsabilità:** Legacy record did not match the strict supported grammar.

<!-- symbol:keys_ng.errors:ReferenceError -->
#### `ReferenceError`

**Tipo:** classe  
**Righe:** 21-22  
**Basi:** `KeysNGError`  
**Responsabilità:** An entry cross-reference was invalid, broken, or cyclic.

### `keys_ng.gui.main`

GUI desktop PySide6, inclusi dialoghi, pannelli per vault, menu e orchestrazione multi-vault.

**Sorgente:** `src/keys_ng/gui/main.py`  
**Simboli eseguibili:** 106

**Dipendenze dirette del modulo:** `__future__`, `argparse`, `keys_ng`, `keys_ng.crypto.factory`, `keys_ng.i18n`, `keys_ng.migration.keepassxc`, `keys_ng.migration.keepassxc_export`, `keys_ng.models`, `keys_ng.platform.app_identity`, `keys_ng.platform.desktop_integration`, `keys_ng.services.actions`, `keys_ng.services.clipboard`, `keys_ng.services.diagnostics`, `keys_ng.services.entry_editor`, `keys_ng.services.passwords`, `keys_ng.services.qr`, `keys_ng.services.ssh_options`, `keys_ng.services.totp`, `keys_ng.services.trusted_signers`, `keys_ng.services.vault_init`, `keys_ng.storage.inbox`, `keys_ng.storage.settings`, `keys_ng.storage.vault`, `pathlib`, `sys`, `time`

<!-- symbol:keys_ng.gui.main:main -->
#### `main`

**Tipo:** funzione/metodo  
**Righe:** 31-1635  
**Firma:** `def main() -> None`  
**Scopo:** Implementa l'operazione `main` in questo modulo.

**Chiamate dirette osservate nel corpo:** `AppSettings.load`, `EntryDialog`, `EntryDraft`, `HelpDialog`, `InboxDialog`, `KeePassXCImportDialog`, `MainWindow`, `NewVaultWizard`, `PasswordGeneratorDialog`, `Path`, `Path.home`, `QApplication`, `QApplication.clipboard`, `QApplication.focusWidget`, `QCheckBox`, `QComboBox`, `QDialogButtonBox`, `QDoubleSpinBox`, `QFileDialog.getExistingDirectory`, `QFileDialog.getOpenFileName`, `QFileDialog.getSaveFileName`, `QFormLayout`, `QHBoxLayout`, `QIcon.fromTheme`, `QInputDialog.getItem`, `QInputDialog.getText`, `QKeySequence`, `QLabel`, `QLineEdit`, `QListWidget`, `QMessageBox.critical`, `QMessageBox.information`, `QMessageBox.question`, `QMessageBox.warning`, `QPushButton`, `QShortcut`, `QSpinBox`, `QStackedWidget`, `QTabWidget`, `QTextBrowser`, `QTextEdit`, `QTimer`, `QTreeWidgetItem`, `QVBoxLayout`, `QWidget`, `QWizardPage`, `SettingsDialog`, `SystemExit`, `TrustedSignersDialog`, `ValueError`, `Vault`, `VaultInitRequest`, `VaultPane`, `VaultTree`, `_`, `__init__`, `action.setEnabled`, `action.setToolTip`, `action.triggered.connect`, `addMenu`, `add_button.clicked.connect`, `add_trusted_signer`, `app.exec`, `apply_qt_identity`, `argparse.ArgumentParser`, `authorize_button.clicked.connect`, `available_vault_keys`, `backend.diagnose`, `bool`, `box.toggled.connect`, `browse.clicked.connect`, `browser.setMarkdown`, `browser.setOpenExternalLinks`, `build_entry_from_draft`, `build_otpauth_uri`, `buttons.accepted.connect`, `buttons.addStretch`, `buttons.addWidget`, `buttons.rejected.connect`, `ch.isalnum`, `clear`, `clipboard_form.addRow`, `close_button.clicked.connect`, `close_buttons.rejected.connect`, `configure_diagnostics`, `configure_language`, `configure_process_identity`, `copy_secret_qt`, `create_button.clicked.connect`, `create_crypto_backend`, `create_vault`, `current.data`, `current.text`, `current_language`, `data`, `delete_button.clicked.connect`, `delete_inbox_item`, `dialog.apply`, `dialog.build_entry`, `dialog.exec`, `dialog.value`, `elapsed_ms`, `eligible_signing_keys`, `empty_label.setAlignment`, `empty_layout.addStretch`, `empty_layout.addWidget`, `ensure_user_desktop_integration`, `entry_menu.addSeparator`, `event.accept`, `event.position`, `exec`, `expanduser`, `export_entry_xml`, `export_vault_xml`, `failures.append`, `files`, `float`, `focus.copy`, `focus.hasSelectedText`, `focus.textCursor`, `folder_widgets.get`, `form.addRow`, `format`, `format_import_report`, `format_ssh_options`, `general_form.addRow`, `generate_password`, `generate_totp`, `get_logger`, `getattr`, `hasSelection`, `hasattr`, `help_label`, `help_root.joinpath`, `icon.isNull`, `image`, `image.isNull`, `import_button.clicked.connect`, `import_inbox_item`, `import_keepassxc`, `import_trusted_button.clicked.connect`, `inspect_inbox`, `int`, `isinstance`, `item.data`, `item.flags`, `item.setData`, `item.setFlags`, `item.setIcon`, `join`, `joinpath`, `key_button.clicked.connect`, `key_layout.addWidget`, `key_layout.setContentsMargins`, `keys_form.addRow`, `keys_page.setSubTitle`, `keys_page.setTitle`, `label.setStyleSheet`, `label.setWordWrap`, `labels.index`, `launch_action`, `layout.addLayout`, `layout.addWidget`, `left.addLayout`, `left.addWidget`, `len`, `line.strip`, `list`, `list_trusted_signers`, `location.setSubTitle`, `location.setTitle`, `location_layout.addLayout`, `log.debug`, `log.error`, `log.info`, `mapping.get`, `max`, `menu.addAction`, `min`, `name.strip`, `next`, `open_button.clicked.connect`, `options.setSubTitle`, `options.setTitle`, `options_form.addRow`, `pane.clear_details`, `pane.deleteLater`, `pane.reload`, `pane.reset_auto_lock_timer`, `pane.vault.lock`, `parent.addChild`, `parse_totp_qimage`, `parse_totp_qr_file`, `parser.add_argument`, `parser.parse_args`, `password_layout.addWidget`, `password_layout.setContentsMargins`, `paths.get`, `pending_inbox_paths`, `preferences_action.setMenuRole`, `preview_button.clicked.connect`, `print`, `range`, `rdp_form.addRow`, `refresh.clicked.connect`, `refresh_button.clicked.connect`, `remaining.remove`, `remove_button.clicked.connect`, `remove_trusted_signer`, `resolve`, `resource.is_file`, `resource.read_text`, `right.addStretch`, `right.addWidget`, `root_layout.addLayout`, `row.addStretch`, `row.addWidget`, `s.save`, `self._entry_icon`, `self._entry_item`, `self._folder_icon`, `self._folder_item`, `self._lines`, `self._menu_action`, `self._run`, `self._status_text`, `self._sync_empty_state`, `self._theme_icon`, `self.accept`, `self.action_type_combo.addItem`, `self.action_type_combo.currentData`, `self.action_type_combo.currentIndexChanged.connect`, `self.action_type_combo.findData`, `self.action_type_combo.setCurrentIndex`, `self.active_pane`, `self.activity`, `self.addPage`, `self.ambiguous.isChecked`, `self.ambiguous.setChecked`, `self.auto_lock_spin.setRange`, `self.auto_lock_spin.setSuffix`, `self.auto_lock_spin.setValue`, `self.auto_lock_spin.value`, `self.auto_lock_timer.setSingleShot`, `self.auto_lock_timer.start`, `self.auto_lock_timer.timeout.connect`, `self.build_menus`, `self.call_active`, `self.clear_details`, `self.close_vault`, `self.copy_notes.clicked.connect`, `self.copy_otp.clicked.connect`, `self.copy_otp.setToolTip`, `self.copy_password.clicked.connect`, `self.copy_password.setToolTip`, `self.copy_url.clicked.connect`, `self.copy_url.setToolTip`, `self.copy_username.clicked.connect`, `self.copy_username.setToolTip`, `self.copy_uuid.clicked.connect`, `self.copy_uuid.setToolTip`, `self.crypto_combo.addItem`, `self.crypto_combo.currentData`, `self.crypto_combo.findData`, `self.crypto_combo.setCurrentIndex`, `self.currentIdChanged.connect`, `self.currentItem`, `self.delete_button.clicked.connect`, `self.delete_folder_button.clicked.connect`, `self.details.clear`, `self.details.setText`, `self.details.setWordWrap`, `self.digits.isChecked`, `self.digits.setChecked`, `self.edit_button.clicked.connect`, `self.entries.addTopLevelItem`, `self.entries.clear`, `self.entries.collapseAll`, `self.entries.currentItemChanged.connect`, `self.entries.expandAll`, `self.entries.itemDoubleClicked.connect`, `self.entries.setDragEnabled`, `self.folder_combo.addItem`, `self.folder_combo.currentData`, `self.folder_combo.findData`, `self.folder_combo.setCurrentIndex`, `self.gpg_path_edit.setPlaceholderText`, `self.gpg_path_edit.text`, `self.gpgconf_path_edit.setPlaceholderText`, `self.gpgconf_path_edit.text`, `self.hard_lock_button.clicked.connect`, `self.host_edit.setVisible`, `self.host_edit.text`, `self.host_label.setVisible`, `self.itemAt`, `self.key_file_edit.setText`, `self.key_file_edit.text`, `self.language_combo.addItem`, `self.language_combo.currentData`, `self.language_combo.findData`, `self.language_combo.setCurrentIndex`, `self.length.setRange`, `self.length.setValue`, `self.length.value`, `self.length.valueChanged.connect`, `self.list.addItem`, `self.list.clear`, `self.list.count`, `self.list.currentItem`, `self.list.currentRow`, `self.list.currentRowChanged.connect`, `self.list.item`, `self.list.setCurrentRow`, `self.lock`, `self.lock_button.clicked.connect`, `self.lower.isChecked`, `self.lower.setChecked`, `self.menuBar`, `self.new_button.clicked.connect`, `self.new_folder_button.clicked.connect`, `self.no_password.isChecked`, `self.notes.clear`, `self.notes.setMinimumHeight`, `self.notes.setReadOnly`, `self.notes.setText`, `self.notes.setToolTip`, `self.notes_edit.toPlainText`, `self.on_move`, `self.on_reload`, `self.open_action.clicked.connect`, `self.open_action.setToolTip`, `self.open_action_clicked`, `self.open_vault`, `self.otp.clear`, `self.otp.setText`, `self.password_edit.setEchoMode`, `self.password_edit.setText`, `self.password_edit.setToolTip`, `self.password_edit.text`, `self.password_generate.clicked.connect`, `self.password_generate.setToolTip`, `self.password_timeout_spin.setRange`, `self.password_timeout_spin.setSuffix`, `self.password_timeout_spin.setValue`, `self.password_timeout_spin.value`, `self.password_toggle.setCheckable`, `self.password_toggle.setText`, `self.password_toggle.setToolTip`, `self.password_toggle.toggled.connect`, `self.path_edit.setText`, `self.path_edit.text`, `self.path_label.clear`, `self.path_label.setText`, `self.port_edit.setPlaceholderText`, `self.port_edit.setVisible`, `self.port_edit.text`, `self.port_label.setVisible`, `self.preview.setReadOnly`, `self.preview.setText`, `self.preview.text`, `self.privacy_combo.addItem`, `self.privacy_combo.currentData`, `self.privacy_combo.setCurrentIndex`, `self.qr_button.clicked.connect`, `self.qr_clipboard_button.clicked.connect`, `self.rdp_linux_client_edit.text`, `self.rdp_linux_options_edit.setMaximumHeight`, `self.rdp_linux_options_edit.setPlainText`, `self.rdp_macos_client_edit.text`, `self.rdp_macos_options_edit.setMaximumHeight`, `self.rdp_macos_options_edit.setPlainText`, `self.rdp_windows_client_edit.text`, `self.rdp_windows_options_edit.setMaximumHeight`, `self.rdp_windows_options_edit.setPlainText`, `self.recent_menu.aboutToShow.connect`, `self.recent_menu.addAction`, `self.recent_menu.clear`, `self.recipient_combo.addItem`, `self.recipient_combo.currentData`, `self.refresh`, `self.refresh_otp`, `self.refresh_recent_menu`, `self.regenerate`, `self.reload`, `self.rename_folder_button.clicked.connect`, `self.report.setPlaceholderText`, `self.report.setPlainText`, `self.report.setReadOnly`, `self.require_signature.isChecked`, `self.require_signature.setChecked`, `self.resize`, `self.search.selectAll`, `self.search.setClearButtonEnabled`, `self.search.setFocus`, `self.search.setPlaceholderText`, `self.search.setToolTip`, `self.search.text`, `self.search.textChanged.connect`, `self.search_timer.setInterval`, `self.search_timer.setSingleShot`, `self.search_timer.start`, `self.search_timer.timeout.connect`, `self.setAcceptDrops`, `self.setCentralWidget`, `self.setDefaultDropAction`, `self.setDragDropMode`, `self.setDragEnabled`, `self.setDropIndicatorShown`, `self.setHeaderHidden`, `self.setLayout`, `self.setWindowTitle`, `self.shortcuts.append`, `self.show_help`, `self.show_inbox`, `self.signer_combo.addItem`, `self.signer_combo.currentData`, `self.source_edit.setText`, `self.source_edit.text`, `self.ssh_options_edit.setMaximumHeight`, `self.ssh_options_edit.setPlaceholderText`, `self.ssh_options_edit.setPlainText`, `self.ssh_options_edit.setText`, `self.ssh_options_edit.setVisible`, `self.ssh_options_edit.text`, `self.ssh_options_label.setVisible`, `self.ssh_terminal_edit.text`, `self.ssh_x11_combo.addItem`, `self.ssh_x11_combo.currentData`, `self.ssh_x11_combo.findData`, `self.ssh_x11_combo.setCurrentIndex`, `self.ssh_x11_combo.setVisible`, `self.ssh_x11_label.setVisible`, `self.stack.addWidget`, `self.stack.setCurrentWidget`, `self.statusBar`, `self.status_message`, `self.style`, `self.summary_label.setText`, `self.summary_label.setWordWrap`, `self.symbols.isChecked`, `self.symbols.setChecked`, `self.tabs.addTab`, `self.tabs.count`, `self.tabs.currentChanged.connect`, `self.tabs.currentIndex`, `self.tabs.currentWidget`, `self.tabs.removeTab`, `self.tabs.setCurrentIndex`, `self.tabs.setMovable`, `self.tabs.setTabPosition`, `self.tabs.setTabToolTip`, `self.tabs.setTabsClosable`, `self.tabs.tabCloseRequested.connect`, `self.tabs.widget`, `self.tags_edit.text`, `self.timer.start`, `self.timer.timeout.connect`, `self.title.clear`, `self.title.setText`, `self.title_edit.text`, `self.totp_edit.setText`, `self.totp_edit.text`, `self.totp_secret_edit.setEchoMode`, `self.totp_secret_edit.setText`, `self.totp_secret_edit.text`, `self.totp_timeout_spin.setRange`, `self.totp_timeout_spin.setSuffix`, `self.totp_timeout_spin.setValue`, `self.totp_timeout_spin.value`, `self.tree_combo.addItem`, `self.tree_combo.currentData`, `self.tree_combo.findData`, `self.tree_combo.setCurrentIndex`, `self.tui_notice_background_edit.setPlaceholderText`, `self.tui_notice_background_edit.text`, `self.tui_notice_foreground_edit.setPlaceholderText`, `self.tui_notice_foreground_edit.text`, `self.tui_notice_seconds_spin.setRange`, `self.tui_notice_seconds_spin.setSingleStep`, `self.tui_notice_seconds_spin.setSuffix`, `self.tui_notice_seconds_spin.setValue`, `self.tui_notice_seconds_spin.value`, `self.unlock_button.clicked.connect`, `self.update_action_fields`, `self.update_window_title`, `self.upper.isChecked`, `self.upper.setChecked`, `self.url_edit.setVisible`, `self.url_edit.text`, `self.url_label.setVisible`, `self.username.clear`, `self.username.setText`, `self.username_edit.setToolTip`, `self.username_edit.text`, `self.uuid_label.clear`, `self.uuid_label.setText`, `self.vault.create_folder`, `self.vault.delete_entry`, `self.vault.delete_folder`, `self.vault.folder_path`, `self.vault.folder_paths`, `self.vault.get_entry`, `self.vault.get_folder`, `self.vault.list_folders`, `self.vault.list_items`, `self.vault.lock`, `self.vault.move_entry`, `self.vault.move_folder`, `self.vault.rename_folder`, `self.vault.resolved_action`, `self.vault.resolved_password`, `self.vault.resolved_username`, `self.vault.save_entry`, `self.vault.search`, `self.vault.unlock`, `self.window`, `self.yubikey_edit.setPlaceholderText`, `self.yubikey_edit.text`, `set`, `setData`, `settings.remember_vault`, `settings.save`, `shortcut.activated.connect`, `shortcut.setContext`, `showMessage`, `source_button.clicked.connect`, `source_layout.addWidget`, `source_layout.setContentsMargins`, `splitlines`, `ssh_form.addRow`, `standardIcon`, `str`, `strip`, `summary.setSubTitle`, `summary.setTitle`, `summary_layout.addWidget`, `super`, `tabs.addTab`, `tabs.count`, `tabs.setCurrentIndex`, `target.data`, `target.parent`, `time.perf_counter`, `toPoint`, `toolbar1.addWidget`, `toolbar2.addWidget`, `type`, `vault.crypto.hard_lock`, `vault_menu.addMenu`, `vault_menu.addSeparator`, `verify_gpg.clicked.connect`, `widget.toPlainText`, `window.hard_lock_all`, `window.resize`, `window.setWindowIcon`, `window.show`, `window.statusBar`, `wizard.exec`, `wizard.request`, `write_export`.

**Eccezioni sollevate esplicitamente:** `SystemExit`, `ValueError`.

**Attributi oggetto modificati:** `s.auto_lock_timeout`, `s.clipboard_password_timeout`, `s.clipboard_totp_timeout`, `s.crypto_backend`, `s.gpg_executable`, `s.gpgconf_executable`, `s.language`, `s.rdp_linux_client`, `s.rdp_linux_options`, `s.rdp_macos_client`, `s.rdp_macos_options`, `s.rdp_windows_client`, `s.rdp_windows_options`, `s.ssh_terminal`, `s.ssh_terminal_options`, `s.tree_startup_view`, `s.tui_clipboard_notice_background`, `s.tui_clipboard_notice_foreground`, `s.tui_clipboard_notice_seconds`, `self._choices`, `self.action_type_combo`, `self.ambiguous`, `self.app_settings`, `self.auto_lock_spin`, `self.auto_lock_timer`, `self.copy_notes`, `self.copy_otp`, `self.copy_password`, `self.copy_url`, `self.copy_username`, `self.copy_uuid`, `self.crypto`, `self.crypto_combo`, `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.delete_button`, `self.delete_folder_button`, `self.details`, `self.digits`, `self.edit_button`, `self.empty_page`, `self.entries`, `self.entry`, `self.folder_combo`, `self.gpg_path_edit`, `self.gpgconf_path_edit`, `self.hard_lock_button`, `self.host_edit`, `self.host_label`, `self.items`, `self.key_file_edit`, `self.language_combo`, `self.length`, `self.list`, `self.lock_button`, `self.lower`, `self.new_button`, `self.new_folder_button`, `self.no_password`, `self.notes`, `self.notes_edit`, `self.on_move`, `self.on_reload`, `self.open_action`, `self.otp`, `self.password_edit`, `self.password_generate`, `self.password_timeout_spin`, `self.password_toggle`, `self.path_edit`, `self.path_label`, `self.port_edit`, `self.port_label`, `self.preview`, `self.privacy_combo`, `self.qr_button`, `self.qr_clipboard_button`, `self.rdp_linux_client_edit`, `self.rdp_linux_options_edit`, `self.rdp_macos_client_edit`, `self.rdp_macos_options_edit`, `self.rdp_windows_client_edit`, `self.rdp_windows_options_edit`, `self.recent_menu`, `self.recipient_combo`, `self.rename_folder_button`, `self.report`, `self.require_signature`, `self.search`, `self.search_timer`, `self.shortcuts`, `self.signer_combo`, `self.source_edit`, `self.ssh_options_edit`, `self.ssh_options_label`, `self.ssh_terminal_edit`, `self.ssh_x11_combo`, `self.ssh_x11_label`, `self.stack`, `self.summary_label`, `self.symbols`, `self.tabs`, `self.tags_edit`, `self.timer`, `self.title`, `self.title_edit`, `self.totp_edit`, `self.totp_secret_edit`, `self.totp_timeout_spin`, `self.tree_combo`, `self.tui_notice_background_edit`, `self.tui_notice_foreground_edit`, `self.tui_notice_seconds_spin`, `self.unlock_button`, `self.upper`, `self.url_edit`, `self.url_label`, `self.username`, `self.username_edit`, `self.uuid_label`, `self.vault`, `self.vault_path`, `self.yubikey_edit`.

**Forma del flusso di controllo:** 109 blocchi condizionali, 24 cicli, 36 blocchi try, 0 context manager, 66 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem, cryptography/key-agent, clipboard, parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultTree -->
#### `main.VaultTree`

**Tipo:** classe  
**Righe:** 83-114  
**Basi:** `QTreeWidget`  
**Metodi:** `__init__`, `dropEvent`  
**Responsabilità:** Implementa l'operazione `VaultTree` in questo modulo.

<!-- symbol:keys_ng.gui.main:main.VaultTree.__init__ -->
#### `main.VaultTree.__init__`

**Tipo:** funzione/metodo  
**Righe:** 84-93  
**Firma:** `def __init__(self, on_move, on_reload, parent=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `__init__`, `self.setAcceptDrops`, `self.setDefaultDropAction`, `self.setDragDropMode`, `self.setDragEnabled`, `self.setDropIndicatorShown`, `self.setHeaderHidden`, `super`.

**Attributi oggetto modificati:** `self.on_move`, `self.on_reload`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultTree.dropEvent -->
#### `main.VaultTree.dropEvent`

**Tipo:** funzione/metodo  
**Righe:** 95-114  
**Firma:** `def dropEvent(self, event) -> None`  
**Scopo:** Implementa l'operazione `dropEvent` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `_`, `data`, `event.accept`, `event.position`, `item.data`, `self.currentItem`, `self.itemAt`, `self.on_move`, `self.on_reload`, `str`, `target.data`, `target.parent`, `toPoint`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.PasswordGeneratorDialog -->
#### `main.PasswordGeneratorDialog`

**Tipo:** classe  
**Righe:** 116-146  
**Basi:** `QDialog`  
**Metodi:** `__init__`, `regenerate`, `value`  
**Responsabilità:** Implementa l'operazione `PasswordGeneratorDialog` in questo modulo.

<!-- symbol:keys_ng.gui.main:main.PasswordGeneratorDialog.__init__ -->
#### `main.PasswordGeneratorDialog.__init__`

**Tipo:** funzione/metodo  
**Righe:** 117-136  
**Firma:** `def __init__(self, parent=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QCheckBox`, `QDialogButtonBox`, `QFormLayout`, `QLineEdit`, `QPushButton`, `QSpinBox`, `QVBoxLayout`, `_`, `__init__`, `box.toggled.connect`, `buttons.accepted.connect`, `buttons.rejected.connect`, `form.addRow`, `layout.addLayout`, `layout.addWidget`, `refresh.clicked.connect`, `self.ambiguous.setChecked`, `self.digits.setChecked`, `self.length.setRange`, `self.length.setValue`, `self.length.valueChanged.connect`, `self.lower.setChecked`, `self.preview.setReadOnly`, `self.regenerate`, `self.setWindowTitle`, `self.symbols.setChecked`, `self.upper.setChecked`, `super`.

**Attributi oggetto modificati:** `self.ambiguous`, `self.digits`, `self.length`, `self.lower`, `self.preview`, `self.symbols`, `self.upper`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.PasswordGeneratorDialog.regenerate -->
#### `main.PasswordGeneratorDialog.regenerate`

**Tipo:** funzione/metodo  
**Righe:** 137-144  
**Firma:** `def regenerate(self) -> None`  
**Scopo:** Implementa l'operazione `regenerate` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `generate_password`, `self.ambiguous.isChecked`, `self.digits.isChecked`, `self.length.value`, `self.lower.isChecked`, `self.preview.setText`, `self.symbols.isChecked`, `self.upper.isChecked`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.PasswordGeneratorDialog.value -->
#### `main.PasswordGeneratorDialog.value`

**Tipo:** funzione/metodo  
**Righe:** 145-146  
**Firma:** `def value(self) -> str`  
**Scopo:** Implementa l'operazione `value` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.preview.text`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.EntryDialog -->
#### `main.EntryDialog`

**Tipo:** classe  
**Righe:** 148-330  
**Basi:** `QDialog`  
**Metodi:** `__init__`, `toggle_password_visibility`, `generate_password_value`, `update_action_fields`, `import_qr`, `import_qr_clipboard`, `build_entry`  
**Responsabilità:** Implementa l'operazione `EntryDialog` in questo modulo.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.__init__ -->
#### `main.EntryDialog.__init__`

**Tipo:** funzione/metodo  
**Righe:** 151-255  
**Firma:** `def __init__(self, vault_obj: Vault, parent=None, entry: Entry | None=None, default_folder_id: str | None=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QComboBox`, `QDialogButtonBox`, `QFormLayout`, `QHBoxLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QTextEdit`, `QVBoxLayout`, `QWidget`, `_`, `__init__`, `build_otpauth_uri`, `buttons.accepted.connect`, `buttons.rejected.connect`, `form.addRow`, `format_ssh_options`, `join`, `layout.addLayout`, `layout.addWidget`, `next`, `password_layout.addWidget`, `password_layout.setContentsMargins`, `self.action_type_combo.addItem`, `self.action_type_combo.currentIndexChanged.connect`, `self.action_type_combo.findData`, `self.action_type_combo.setCurrentIndex`, `self.folder_combo.addItem`, `self.folder_combo.findData`, `self.folder_combo.setCurrentIndex`, `self.password_edit.setEchoMode`, `self.password_edit.setToolTip`, `self.password_generate.clicked.connect`, `self.password_generate.setToolTip`, `self.password_toggle.setCheckable`, `self.password_toggle.setToolTip`, `self.password_toggle.toggled.connect`, `self.qr_button.clicked.connect`, `self.qr_clipboard_button.clicked.connect`, `self.setWindowTitle`, `self.ssh_options_edit.setPlaceholderText`, `self.ssh_options_edit.setText`, `self.ssh_x11_combo.addItem`, `self.ssh_x11_combo.findData`, `self.ssh_x11_combo.setCurrentIndex`, `self.totp_edit.setText`, `self.totp_secret_edit.setEchoMode`, `self.totp_secret_edit.setText`, `self.update_action_fields`, `self.username_edit.setToolTip`, `self.vault.folder_path`, `self.vault.list_folders`, `str`, `super`.

**Attributi oggetto modificati:** `self.action_type_combo`, `self.entry`, `self.folder_combo`, `self.host_edit`, `self.host_label`, `self.notes_edit`, `self.password_edit`, `self.password_generate`, `self.password_toggle`, `self.port_edit`, `self.port_label`, `self.qr_button`, `self.qr_clipboard_button`, `self.ssh_options_edit`, `self.ssh_options_label`, `self.ssh_x11_combo`, `self.ssh_x11_label`, `self.tags_edit`, `self.title_edit`, `self.totp_edit`, `self.totp_secret_edit`, `self.url_edit`, `self.url_label`, `self.username_edit`, `self.vault`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.toggle_password_visibility -->
#### `main.EntryDialog.toggle_password_visibility`

**Tipo:** funzione/metodo  
**Righe:** 257-259  
**Firma:** `def toggle_password_visibility(self, visible: bool) -> None`  
**Scopo:** Implementa l'operazione `toggle_password_visibility` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `self.password_edit.setEchoMode`, `self.password_toggle.setText`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.generate_password_value -->
#### `main.EntryDialog.generate_password_value`

**Tipo:** funzione/metodo  
**Righe:** 261-264  
**Firma:** `def generate_password_value(self) -> None`  
**Scopo:** Implementa l'operazione `generate_password_value` in questo modulo.

**Chiamate dirette osservate nel corpo:** `PasswordGeneratorDialog`, `dialog.exec`, `dialog.value`, `self.password_edit.setText`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.update_action_fields -->
#### `main.EntryDialog.update_action_fields`

**Tipo:** funzione/metodo  
**Righe:** 266-286  
**Firma:** `def update_action_fields(self) -> None`  
**Scopo:** Implementa l'operazione `update_action_fields` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.action_type_combo.currentData`, `self.host_edit.setVisible`, `self.host_label.setVisible`, `self.port_edit.setPlaceholderText`, `self.port_edit.setVisible`, `self.port_label.setVisible`, `self.ssh_options_edit.setVisible`, `self.ssh_options_label.setVisible`, `self.ssh_x11_combo.setVisible`, `self.ssh_x11_label.setVisible`, `self.url_edit.setVisible`, `self.url_label.setVisible`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.import_qr -->
#### `main.EntryDialog.import_qr`

**Tipo:** funzione/metodo  
**Righe:** 288-298  
**Firma:** `def import_qr(self) -> None`  
**Scopo:** Importa `import_qr`.

**Chiamate dirette osservate nel corpo:** `QFileDialog.getOpenFileName`, `QMessageBox.critical`, `_`, `build_otpauth_uri`, `parse_totp_qr_file`, `self.totp_edit.setText`, `self.totp_secret_edit.setText`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.import_qr_clipboard -->
#### `main.EntryDialog.import_qr_clipboard`

**Tipo:** funzione/metodo  
**Righe:** 300-311  
**Firma:** `def import_qr_clipboard(self) -> None`  
**Scopo:** Importa `import_qr_clipboard`.

**Chiamate dirette osservate nel corpo:** `QApplication.clipboard`, `QMessageBox.critical`, `ValueError`, `_`, `build_otpauth_uri`, `image`, `image.isNull`, `parse_totp_qimage`, `self.totp_edit.setText`, `self.totp_secret_edit.setText`, `str`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.EntryDialog.build_entry -->
#### `main.EntryDialog.build_entry`

**Tipo:** funzione/metodo  
**Righe:** 313-330  
**Firma:** `def build_entry(self) -> Entry`  
**Scopo:** Costruisce `build_entry`.

**Chiamate dirette osservate nel corpo:** `EntryDraft`, `build_entry_from_draft`, `self.action_type_combo.currentData`, `self.folder_combo.currentData`, `self.host_edit.text`, `self.notes_edit.toPlainText`, `self.password_edit.text`, `self.port_edit.text`, `self.ssh_options_edit.text`, `self.ssh_x11_combo.currentData`, `self.tags_edit.text`, `self.title_edit.text`, `self.totp_edit.text`, `self.totp_secret_edit.text`, `self.url_edit.text`, `self.username_edit.text`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.HelpDialog -->
#### `main.HelpDialog`

**Tipo:** classe  
**Righe:** 332-364  
**Basi:** `QDialog`  
**Metodi:** `__init__`  
**Responsabilità:** Implementa l'operazione `HelpDialog` in questo modulo.

<!-- symbol:keys_ng.gui.main:main.HelpDialog.__init__ -->
#### `main.HelpDialog.__init__`

**Tipo:** funzione/metodo  
**Righe:** 333-364  
**Firma:** `def __init__(self, parent=None, initial_tab: int=0) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QDialogButtonBox`, `QTabWidget`, `QTextBrowser`, `QVBoxLayout`, `_`, `__init__`, `browser.setMarkdown`, `browser.setOpenExternalLinks`, `close_buttons.rejected.connect`, `current_language`, `files`, `format`, `help_root.joinpath`, `joinpath`, `layout.addWidget`, `max`, `min`, `resource.is_file`, `resource.read_text`, `self.resize`, `self.setWindowTitle`, `super`, `tabs.addTab`, `tabs.count`, `tabs.setCurrentIndex`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog -->
#### `main.KeePassXCImportDialog`

**Tipo:** classe  
**Righe:** 366-443  
**Basi:** `QDialog`  
**Metodi:** `__init__`, `browse_source`, `browse_key_file`, `_run`, `preview_import`, `perform_import`  
**Responsabilità:** Preview and import a KeePassXC KDBX/XML source into an open vault.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.__init__ -->
#### `main.KeePassXCImportDialog.__init__`

**Tipo:** funzione/metodo  
**Righe:** 369-405  
**Firma:** `def __init__(self, vault_obj: Vault, parent=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QCheckBox`, `QFormLayout`, `QHBoxLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QTextEdit`, `QVBoxLayout`, `QWidget`, `_`, `__init__`, `close_button.clicked.connect`, `form.addRow`, `import_button.clicked.connect`, `key_button.clicked.connect`, `key_layout.addWidget`, `key_layout.setContentsMargins`, `layout.addLayout`, `layout.addWidget`, `preview_button.clicked.connect`, `row.addStretch`, `row.addWidget`, `self.password_edit.setEchoMode`, `self.password_edit.setToolTip`, `self.report.setPlaceholderText`, `self.report.setReadOnly`, `self.resize`, `self.setWindowTitle`, `self.yubikey_edit.setPlaceholderText`, `source_button.clicked.connect`, `source_layout.addWidget`, `source_layout.setContentsMargins`, `super`.

**Attributi oggetto modificati:** `self.key_file_edit`, `self.no_password`, `self.password_edit`, `self.report`, `self.source_edit`, `self.vault`, `self.yubikey_edit`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.browse_source -->
#### `main.KeePassXCImportDialog.browse_source`

**Tipo:** funzione/metodo  
**Righe:** 407-409  
**Firma:** `def browse_source(self) -> None`  
**Scopo:** Implementa l'operazione `browse_source` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path.home`, `QFileDialog.getOpenFileName`, `_`, `self.source_edit.setText`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.browse_key_file -->
#### `main.KeePassXCImportDialog.browse_key_file`

**Tipo:** funzione/metodo  
**Righe:** 411-413  
**Firma:** `def browse_key_file(self) -> None`  
**Scopo:** Implementa l'operazione `browse_key_file` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path.home`, `QFileDialog.getOpenFileName`, `_`, `self.key_file_edit.setText`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog._run -->
#### `main.KeePassXCImportDialog._run`

**Tipo:** funzione/metodo  
**Righe:** 415-425  
**Firma:** `def _run(self, dry_run: bool)`  
**Scopo:** Helper interno che implementa `_run`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `_`, `import_keepassxc`, `self.key_file_edit.text`, `self.no_password.isChecked`, `self.password_edit.text`, `self.source_edit.text`, `self.yubikey_edit.text`, `strip`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.preview_import -->
#### `main.KeePassXCImportDialog.preview_import`

**Tipo:** funzione/metodo  
**Righe:** 427-432  
**Firma:** `def preview_import(self) -> None`  
**Scopo:** Implementa l'operazione `preview_import` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `_`, `format_import_report`, `self._run`, `self.report.setPlainText`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.KeePassXCImportDialog.perform_import -->
#### `main.KeePassXCImportDialog.perform_import`

**Tipo:** funzione/metodo  
**Righe:** 434-443  
**Firma:** `def perform_import(self) -> None`  
**Scopo:** Implementa l'operazione `perform_import` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `QMessageBox.information`, `QMessageBox.warning`, `_`, `format_import_report`, `self._run`, `self.accept`, `self.report.setPlainText`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog -->
#### `main.TrustedSignersDialog`

**Tipo:** classe  
**Righe:** 445-500  
**Basi:** `QDialog`  
**Metodi:** `__init__`, `refresh`, `add_signer`, `remove_signer`  
**Responsabilità:** Implementa l'operazione `TrustedSignersDialog` in questo modulo.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog.__init__ -->
#### `main.TrustedSignersDialog.__init__`

**Tipo:** funzione/metodo  
**Righe:** 446-464  
**Firma:** `def __init__(self, vault: Vault, parent=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QHBoxLayout`, `QLabel`, `QListWidget`, `QPushButton`, `QVBoxLayout`, `_`, `__init__`, `add_button.clicked.connect`, `buttons.addStretch`, `buttons.addWidget`, `close_button.clicked.connect`, `layout.addLayout`, `layout.addWidget`, `remove_button.clicked.connect`, `self.refresh`, `self.resize`, `self.setWindowTitle`, `super`.

**Attributi oggetto modificati:** `self.list`, `self.vault`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog.refresh -->
#### `main.TrustedSignersDialog.refresh`

**Tipo:** funzione/metodo  
**Righe:** 466-471  
**Firma:** `def refresh(self) -> None`  
**Scopo:** Implementa l'operazione `refresh` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `list_trusted_signers`, `self.list.addItem`, `self.list.clear`, `self.list.count`, `self.list.item`, `setData`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog.add_signer -->
#### `main.TrustedSignersDialog.add_signer`

**Tipo:** funzione/metodo  
**Righe:** 473-487  
**Firma:** `def add_signer(self) -> None`  
**Scopo:** Implementa l'operazione `add_signer` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QInputDialog.getItem`, `QMessageBox.information`, `QMessageBox.question`, `_`, `add_trusted_signer`, `eligible_signing_keys`, `format`, `labels.index`, `list_trusted_signers`, `self.refresh`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.TrustedSignersDialog.remove_signer -->
#### `main.TrustedSignersDialog.remove_signer`

**Tipo:** funzione/metodo  
**Righe:** 489-500  
**Firma:** `def remove_signer(self) -> None`  
**Scopo:** Implementa l'operazione `remove_signer` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `QMessageBox.question`, `_`, `format`, `item.data`, `remove_trusted_signer`, `self.list.currentItem`, `self.refresh`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.InboxDialog -->
#### `main.InboxDialog`

**Tipo:** classe  
**Righe:** 503-614  
**Basi:** `QDialog`  
**Metodi:** `__init__`, `_status_text`, `refresh`, `show_details`, `import_selected`, `import_all_trusted`, `authorize_selected`, `delete_selected`  
**Responsabilità:** Implementa l'operazione `InboxDialog` in questo modulo.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.__init__ -->
#### `main.InboxDialog.__init__`

**Tipo:** funzione/metodo  
**Righe:** 504-534  
**Firma:** `def __init__(self, vault: Vault, parent=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QHBoxLayout`, `QLabel`, `QListWidget`, `QPushButton`, `QVBoxLayout`, `_`, `__init__`, `authorize_button.clicked.connect`, `close_button.clicked.connect`, `delete_button.clicked.connect`, `import_button.clicked.connect`, `import_trusted_button.clicked.connect`, `layout.addLayout`, `layout.addWidget`, `refresh_button.clicked.connect`, `row.addStretch`, `row.addWidget`, `self.details.setWordWrap`, `self.list.currentRowChanged.connect`, `self.refresh`, `self.resize`, `self.setWindowTitle`, `super`.

**Attributi oggetto modificati:** `self.details`, `self.items`, `self.list`, `self.vault`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.InboxDialog._status_text -->
#### `main.InboxDialog._status_text`

**Tipo:** funzione/metodo  
**Righe:** 536-545  
**Firma:** `def _status_text(self, item) -> str`  
**Scopo:** Helper interno che implementa `_status_text`.

**Chiamate dirette osservate nel corpo:** `_`, `mapping.get`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.refresh -->
#### `main.InboxDialog.refresh`

**Tipo:** funzione/metodo  
**Righe:** 547-556  
**Firma:** `def refresh(self) -> None`  
**Scopo:** Implementa l'operazione `refresh` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `inspect_inbox`, `self._status_text`, `self.details.setText`, `self.list.addItem`, `self.list.clear`, `self.list.setCurrentRow`.

**Attributi oggetto modificati:** `self.items`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.show_details -->
#### `main.InboxDialog.show_details`

**Tipo:** funzione/metodo  
**Righe:** 558-566  
**Firma:** `def show_details(self, row: int) -> None`  
**Scopo:** Implementa l'operazione `show_details` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `format`, `len`, `self._status_text`, `self.details.clear`, `self.details.setText`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.import_selected -->
#### `main.InboxDialog.import_selected`

**Tipo:** funzione/metodo  
**Righe:** 568-581  
**Firma:** `def import_selected(self) -> None`  
**Scopo:** Importa `import_selected`.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `QMessageBox.warning`, `_`, `import_inbox_item`, `self.list.currentRow`, `self.refresh`, `str`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.import_all_trusted -->
#### `main.InboxDialog.import_all_trusted`

**Tipo:** funzione/metodo  
**Righe:** 583-590  
**Firma:** `def import_all_trusted(self) -> None`  
**Scopo:** Importa `import_all_trusted`.

**Chiamate dirette osservate nel corpo:** `QMessageBox.warning`, `_`, `failures.append`, `import_inbox_item`, `list`, `self.refresh`, `type`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.authorize_selected -->
#### `main.InboxDialog.authorize_selected`

**Tipo:** funzione/metodo  
**Righe:** 592-604  
**Firma:** `def authorize_selected(self) -> None`  
**Scopo:** Implementa l'operazione `authorize_selected` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `QMessageBox.information`, `QMessageBox.question`, `_`, `add_trusted_signer`, `format`, `self.list.currentRow`, `self.refresh`, `str`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.InboxDialog.delete_selected -->
#### `main.InboxDialog.delete_selected`

**Tipo:** funzione/metodo  
**Righe:** 606-614  
**Firma:** `def delete_selected(self) -> None`  
**Scopo:** Elimina `delete_selected`.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `QMessageBox.warning`, `_`, `delete_inbox_item`, `self.list.currentRow`, `self.refresh`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane -->
#### `main.VaultPane`

**Tipo:** classe  
**Righe:** 616-1075  
**Basi:** `QWidget`  
**Metodi:** `__init__`, `display_name`, `status_message`, `focus_search`, `schedule_search`, `activity`, `_theme_icon`, `_folder_icon`, `_entry_icon`, `_folder_item`, `_entry_item`, `reload`, `select_item`, `clear_details`, `tree_move`, `request_hard_lock`, `lock`, `unlock`, `refresh_otp`, `copy_url_clicked`, `copy_uuid_clicked`, `copy_username_clicked`, `copy_password_clicked`, `copy_notes_clicked`, `copy_otp_clicked`, `open_action_clicked`, `export_entry_keepassxc`, `new_entry`, `edit_entry`, `delete_entry`, `new_folder`, `rename_folder`, `delete_folder`  
**Responsabilità:** Stato e widget GUI per una singola scheda vault con lock indipendente.

<!-- symbol:keys_ng.gui.main:main.VaultPane.__init__ -->
#### `main.VaultPane.__init__`

**Tipo:** funzione/metodo  
**Righe:** 617-728  
**Firma:** `def __init__(self, vault_path: str, parent=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `Path`, `QHBoxLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QTextEdit`, `QTimer`, `QVBoxLayout`, `Vault`, `VaultTree`, `_`, `__init__`, `create_crypto_backend`, `expanduser`, `left.addLayout`, `left.addWidget`, `resolve`, `right.addStretch`, `right.addWidget`, `root_layout.addLayout`, `self.auto_lock_timer.setSingleShot`, `self.auto_lock_timer.start`, `self.auto_lock_timer.timeout.connect`, `self.copy_notes.clicked.connect`, `self.copy_otp.clicked.connect`, `self.copy_otp.setToolTip`, `self.copy_password.clicked.connect`, `self.copy_password.setToolTip`, `self.copy_url.clicked.connect`, `self.copy_url.setToolTip`, `self.copy_username.clicked.connect`, `self.copy_username.setToolTip`, `self.copy_uuid.clicked.connect`, `self.copy_uuid.setToolTip`, `self.delete_button.clicked.connect`, `self.delete_folder_button.clicked.connect`, `self.edit_button.clicked.connect`, `self.entries.currentItemChanged.connect`, `self.entries.itemDoubleClicked.connect`, `self.hard_lock_button.clicked.connect`, `self.lock`, `self.lock_button.clicked.connect`, `self.new_button.clicked.connect`, `self.new_folder_button.clicked.connect`, `self.notes.setMinimumHeight`, `self.notes.setReadOnly`, `self.notes.setToolTip`, `self.open_action.clicked.connect`, `self.open_action.setToolTip`, `self.open_action_clicked`, `self.reload`, `self.rename_folder_button.clicked.connect`, `self.search.setClearButtonEnabled`, `self.search.setPlaceholderText`, `self.search.setToolTip`, `self.search.textChanged.connect`, `self.search_timer.setInterval`, `self.search_timer.setSingleShot`, `self.search_timer.timeout.connect`, `self.setLayout`, `self.timer.start`, `self.timer.timeout.connect`, `self.unlock_button.clicked.connect`, `super`, `toolbar1.addWidget`, `toolbar2.addWidget`.

**Attributi oggetto modificati:** `self.auto_lock_timer`, `self.copy_notes`, `self.copy_otp`, `self.copy_password`, `self.copy_url`, `self.copy_username`, `self.copy_uuid`, `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.delete_button`, `self.delete_folder_button`, `self.edit_button`, `self.entries`, `self.hard_lock_button`, `self.lock_button`, `self.new_button`, `self.new_folder_button`, `self.notes`, `self.open_action`, `self.otp`, `self.path_label`, `self.rename_folder_button`, `self.search`, `self.search_timer`, `self.timer`, `self.title`, `self.unlock_button`, `self.username`, `self.uuid_label`, `self.vault`, `self.vault_path`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.display_name -->
#### `main.VaultPane.display_name`

**Tipo:** funzione/metodo  
**Righe:** 731-732  
**Firma:** `def display_name(self) -> str`  
**Scopo:** Implementa l'operazione `display_name` in questo modulo.

**Chiamate dirette osservate nel corpo:** `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.status_message -->
#### `main.VaultPane.status_message`

**Tipo:** funzione/metodo  
**Righe:** 734-737  
**Firma:** `def status_message(self, message: str, timeout: int=0) -> None`  
**Scopo:** Implementa l'operazione `status_message` in questo modulo.

**Chiamate dirette osservate nel corpo:** `hasattr`, `self.window`, `showMessage`, `window.statusBar`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.focus_search -->
#### `main.VaultPane.focus_search`

**Tipo:** funzione/metodo  
**Righe:** 739-742  
**Firma:** `def focus_search(self) -> None`  
**Scopo:** Implementa l'operazione `focus_search` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.activity`, `self.search.selectAll`, `self.search.setFocus`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.schedule_search -->
#### `main.VaultPane.schedule_search`

**Tipo:** funzione/metodo  
**Righe:** 744-746  
**Firma:** `def schedule_search(self) -> None`  
**Scopo:** Implementa l'operazione `schedule_search` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.activity`, `self.search_timer.start`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.activity -->
#### `main.VaultPane.activity`

**Tipo:** funzione/metodo  
**Righe:** 748-750  
**Firma:** `def activity(self) -> None`  
**Scopo:** Implementa l'operazione `activity` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.auto_lock_timer.start`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane._theme_icon -->
#### `main.VaultPane._theme_icon`

**Tipo:** funzione/metodo  
**Righe:** 752-757  
**Firma:** `def _theme_icon(self, names: tuple[str, ...], fallback) -> QIcon`  
**Scopo:** Helper interno che implementa `_theme_icon`.

**Chiamate dirette osservate nel corpo:** `QIcon.fromTheme`, `icon.isNull`, `self.style`, `standardIcon`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane._folder_icon -->
#### `main.VaultPane._folder_icon`

**Tipo:** funzione/metodo  
**Righe:** 759-760  
**Firma:** `def _folder_icon(self) -> QIcon`  
**Scopo:** Helper interno che implementa `_folder_icon`.

**Chiamate dirette osservate nel corpo:** `self._theme_icon`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane._entry_icon -->
#### `main.VaultPane._entry_icon`

**Tipo:** funzione/metodo  
**Righe:** 762-772  
**Firma:** `def _entry_icon(self, catalog_item) -> QIcon`  
**Scopo:** Helper interno che implementa `_entry_icon`.

**Chiamate dirette osservate nel corpo:** `self._theme_icon`, `set`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 5 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane._folder_item -->
#### `main.VaultPane._folder_item`

**Tipo:** funzione/metodo  
**Righe:** 774-784  
**Firma:** `def _folder_item(self, folder, parent=None)`  
**Scopo:** Helper interno che implementa `_folder_item`.

**Chiamate dirette osservate nel corpo:** `QTreeWidgetItem`, `item.flags`, `item.setData`, `item.setFlags`, `item.setIcon`, `parent.addChild`, `self._folder_icon`, `self.entries.addTopLevelItem`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane._entry_item -->
#### `main.VaultPane._entry_item`

**Tipo:** funzione/metodo  
**Righe:** 786-797  
**Firma:** `def _entry_item(self, catalog_item, parent=None, suffix='')`  
**Scopo:** Helper interno che implementa `_entry_item`.

**Chiamate dirette osservate nel corpo:** `QTreeWidgetItem`, `item.flags`, `item.setData`, `item.setFlags`, `item.setIcon`, `parent.addChild`, `self._entry_icon`, `self.entries.addTopLevelItem`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.reload -->
#### `main.VaultPane.reload`

**Tipo:** funzione/metodo  
**Righe:** 799-833  
**Firma:** `def reload(self) -> None`  
**Scopo:** Implementa l'operazione `reload` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `_`, `bool`, `folder_widgets.get`, `list`, `paths.get`, `remaining.remove`, `self._entry_item`, `self._folder_item`, `self.entries.clear`, `self.entries.collapseAll`, `self.entries.expandAll`, `self.entries.setDragEnabled`, `self.search.text`, `self.vault.folder_paths`, `self.vault.list_folders`, `self.vault.list_items`, `self.vault.search`, `str`, `strip`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 4 cicli, 1 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.select_item -->
#### `main.VaultPane.select_item`

**Tipo:** funzione/metodo  
**Righe:** 835-876  
**Firma:** `def select_item(self, current, _previous) -> None`  
**Scopo:** Implementa l'operazione `select_item` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `_`, `current.data`, `current.text`, `elapsed_ms`, `log.debug`, `log.error`, `log.info`, `self.activity`, `self.notes.clear`, `self.notes.setText`, `self.otp.clear`, `self.path_label.setText`, `self.refresh_otp`, `self.title.setText`, `self.username.clear`, `self.username.setText`, `self.uuid_label.clear`, `self.uuid_label.setText`, `self.vault.folder_path`, `self.vault.get_entry`, `self.vault.resolved_username`, `str`, `time.perf_counter`, `type`.

**Attributi oggetto modificati:** `self.current_entry`, `self.current_folder_id`, `self.current_id`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.clear_details -->
#### `main.VaultPane.clear_details`

**Tipo:** funzione/metodo  
**Righe:** 878-883  
**Firma:** `def clear_details(self) -> None`  
**Scopo:** Implementa l'operazione `clear_details` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.entries.clear`, `self.notes.clear`, `self.otp.clear`, `self.path_label.clear`, `self.title.clear`, `self.username.clear`, `self.uuid_label.clear`.

**Attributi oggetto modificati:** `self.current_entry`, `self.current_folder_id`, `self.current_id`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.tree_move -->
#### `main.VaultPane.tree_move`

**Tipo:** funzione/metodo  
**Righe:** 885-891  
**Firma:** `def tree_move(self, item_type: str, item_id: str, parent_id: str | None) -> None`  
**Scopo:** Implementa l'operazione `tree_move` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.search.text`, `self.vault.move_entry`, `self.vault.move_folder`, `strip`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.request_hard_lock -->
#### `main.VaultPane.request_hard_lock`

**Tipo:** funzione/metodo  
**Righe:** 893-898  
**Firma:** `def request_hard_lock(self) -> None`  
**Scopo:** Implementa l'operazione `request_hard_lock` in questo modulo.

**Chiamate dirette osservate nel corpo:** `hasattr`, `self.lock`, `self.window`, `window.hard_lock_all`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.lock -->
#### `main.VaultPane.lock`

**Tipo:** funzione/metodo  
**Righe:** 900-907  
**Firma:** `def lock(self, hard: bool) -> None`  
**Scopo:** Implementa l'operazione `lock` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QApplication.clipboard`, `QMessageBox.critical`, `_`, `clear`, `self.clear_details`, `self.status_message`, `self.vault.lock`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.unlock -->
#### `main.VaultPane.unlock`

**Tipo:** funzione/metodo  
**Righe:** 909-916  
**Firma:** `def unlock(self) -> None`  
**Scopo:** Implementa l'operazione `unlock` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `_`, `self.activity`, `self.reload`, `self.status_message`, `self.vault.unlock`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.refresh_otp -->
#### `main.VaultPane.refresh_otp`

**Tipo:** funzione/metodo  
**Righe:** 918-923  
**Firma:** `def refresh_otp(self) -> None`  
**Scopo:** Implementa l'operazione `refresh_otp` in questo modulo.

**Chiamate dirette osservate nel corpo:** `generate_totp`, `self.otp.setText`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_url_clicked -->
#### `main.VaultPane.copy_url_clicked`

**Tipo:** funzione/metodo  
**Righe:** 925-932  
**Firma:** `def copy_url_clicked(self) -> None`  
**Scopo:** Copia un valore usando `copy_url_clicked`.

**Chiamate dirette osservate nel corpo:** `_`, `copy_secret_qt`, `next`, `self.activity`, `self.status_message`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_uuid_clicked -->
#### `main.VaultPane.copy_uuid_clicked`

**Tipo:** funzione/metodo  
**Righe:** 934-938  
**Firma:** `def copy_uuid_clicked(self) -> None`  
**Scopo:** Copia un valore usando `copy_uuid_clicked`.

**Chiamate dirette osservate nel corpo:** `_`, `copy_secret_qt`, `self.activity`, `self.status_message`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_username_clicked -->
#### `main.VaultPane.copy_username_clicked`

**Tipo:** funzione/metodo  
**Righe:** 940-950  
**Firma:** `def copy_username_clicked(self) -> None`  
**Scopo:** Copia un valore usando `copy_username_clicked`.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `_`, `copy_secret_qt`, `self.activity`, `self.status_message`, `self.vault.resolved_username`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_password_clicked -->
#### `main.VaultPane.copy_password_clicked`

**Tipo:** funzione/metodo  
**Righe:** 952-961  
**Firma:** `def copy_password_clicked(self) -> None`  
**Scopo:** Copia un valore usando `copy_password_clicked`.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `_`, `copy_secret_qt`, `self.activity`, `self.vault.resolved_password`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_notes_clicked -->
#### `main.VaultPane.copy_notes_clicked`

**Tipo:** funzione/metodo  
**Righe:** 963-967  
**Firma:** `def copy_notes_clicked(self) -> None`  
**Scopo:** Copia un valore usando `copy_notes_clicked`.

**Chiamate dirette osservate nel corpo:** `_`, `copy_secret_qt`, `self.activity`, `self.status_message`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.copy_otp_clicked -->
#### `main.VaultPane.copy_otp_clicked`

**Tipo:** funzione/metodo  
**Righe:** 969-973  
**Firma:** `def copy_otp_clicked(self) -> None`  
**Scopo:** Copia un valore usando `copy_otp_clicked`.

**Chiamate dirette osservate nel corpo:** `copy_secret_qt`, `generate_totp`, `self.activity`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.open_action_clicked -->
#### `main.VaultPane.open_action_clicked`

**Tipo:** funzione/metodo  
**Righe:** 975-981  
**Firma:** `def open_action_clicked(self) -> None`  
**Scopo:** Implementa l'operazione `open_action_clicked` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `_`, `launch_action`, `self.activity`, `self.vault.resolved_action`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.export_entry_keepassxc -->
#### `main.VaultPane.export_entry_keepassxc`

**Tipo:** funzione/metodo  
**Righe:** 983-1002  
**Firma:** `def export_entry_keepassxc(self) -> None`  
**Scopo:** Esporta `export_entry_keepassxc`.

**Chiamate dirette osservate nel corpo:** `QFileDialog.getSaveFileName`, `QMessageBox.critical`, `QMessageBox.warning`, `_`, `ch.isalnum`, `export_entry_xml`, `join`, `self.activity`, `self.status_message`, `str`, `strip`, `write_export`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.new_entry -->
#### `main.VaultPane.new_entry`

**Tipo:** funzione/metodo  
**Righe:** 1004-1014  
**Firma:** `def new_entry(self) -> None`  
**Scopo:** Implementa l'operazione `new_entry` in questo modulo.

**Chiamate dirette osservate nel corpo:** `EntryDialog`, `QMessageBox.critical`, `_`, `dialog.build_entry`, `dialog.exec`, `self.activity`, `self.reload`, `self.vault.save_entry`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.edit_entry -->
#### `main.VaultPane.edit_entry`

**Tipo:** funzione/metodo  
**Righe:** 1016-1026  
**Firma:** `def edit_entry(self) -> None`  
**Scopo:** Implementa l'operazione `edit_entry` in questo modulo.

**Chiamate dirette osservate nel corpo:** `EntryDialog`, `QMessageBox.critical`, `_`, `dialog.build_entry`, `dialog.exec`, `self.activity`, `self.reload`, `self.vault.save_entry`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.delete_entry -->
#### `main.VaultPane.delete_entry`

**Tipo:** funzione/metodo  
**Righe:** 1028-1039  
**Firma:** `def delete_entry(self) -> None`  
**Scopo:** Elimina `delete_entry`.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `QMessageBox.question`, `_`, `self.activity`, `self.clear_details`, `self.reload`, `self.vault.delete_entry`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.new_folder -->
#### `main.VaultPane.new_folder`

**Tipo:** funzione/metodo  
**Righe:** 1041-1051  
**Firma:** `def new_folder(self) -> None`  
**Scopo:** Implementa l'operazione `new_folder` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QInputDialog.getText`, `QMessageBox.critical`, `_`, `name.strip`, `self.activity`, `self.reload`, `self.vault.create_folder`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.rename_folder -->
#### `main.VaultPane.rename_folder`

**Tipo:** funzione/metodo  
**Righe:** 1053-1063  
**Firma:** `def rename_folder(self) -> None`  
**Scopo:** Implementa l'operazione `rename_folder` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QInputDialog.getText`, `QMessageBox.critical`, `_`, `name.strip`, `self.reload`, `self.vault.get_folder`, `self.vault.rename_folder`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.VaultPane.delete_folder -->
#### `main.VaultPane.delete_folder`

**Tipo:** funzione/metodo  
**Righe:** 1065-1075  
**Firma:** `def delete_folder(self) -> None`  
**Scopo:** Elimina `delete_folder`.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `QMessageBox.question`, `_`, `self.clear_details`, `self.reload`, `self.vault.delete_folder`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard -->
#### `main.NewVaultWizard`

**Tipo:** classe  
**Righe:** 1078-1169  
**Basi:** `QWizard`  
**Metodi:** `__init__`, `_browse`, `_update_summary`, `request`  
**Responsabilità:** Guided vault creation using the same initialization service as the CLI.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard.__init__ -->
#### `main.NewVaultWizard.__init__`

**Tipo:** funzione/metodo  
**Righe:** 1081-1138  
**Firma:** `def __init__(self, crypto, parent=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QCheckBox`, `QComboBox`, `QFormLayout`, `QHBoxLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QVBoxLayout`, `QWizardPage`, `_`, `__init__`, `available_vault_keys`, `browse.clicked.connect`, `keys_form.addRow`, `keys_page.setSubTitle`, `keys_page.setTitle`, `location.setSubTitle`, `location.setTitle`, `location_layout.addLayout`, `options.setSubTitle`, `options.setTitle`, `options_form.addRow`, `row.addWidget`, `self.addPage`, `self.currentIdChanged.connect`, `self.privacy_combo.addItem`, `self.privacy_combo.setCurrentIndex`, `self.recipient_combo.addItem`, `self.require_signature.setChecked`, `self.resize`, `self.setWindowTitle`, `self.signer_combo.addItem`, `self.summary_label.setWordWrap`, `summary.setSubTitle`, `summary.setTitle`, `summary_layout.addWidget`, `super`.

**Attributi oggetto modificati:** `self._choices`, `self.crypto`, `self.path_edit`, `self.privacy_combo`, `self.recipient_combo`, `self.require_signature`, `self.signer_combo`, `self.summary_label`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard._browse -->
#### `main.NewVaultWizard._browse`

**Tipo:** funzione/metodo  
**Righe:** 1140-1144  
**Firma:** `def _browse(self) -> None`  
**Scopo:** Helper interno che implementa `_browse`.

**Chiamate dirette osservate nel corpo:** `Path.home`, `QFileDialog.getExistingDirectory`, `_`, `self.path_edit.setText`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard._update_summary -->
#### `main.NewVaultWizard._update_summary`

**Tipo:** funzione/metodo  
**Righe:** 1146-1154  
**Firma:** `def _update_summary(self, _page_id: int) -> None`  
**Scopo:** Helper interno che implementa `_update_summary`.

**Chiamate dirette osservate nel corpo:** `_`, `self.path_edit.text`, `self.privacy_combo.currentData`, `self.recipient_combo.currentData`, `self.signer_combo.currentData`, `self.summary_label.setText`, `str`, `strip`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.NewVaultWizard.request -->
#### `main.NewVaultWizard.request`

**Tipo:** funzione/metodo  
**Righe:** 1156-1169  
**Firma:** `def request(self) -> VaultInitRequest`  
**Scopo:** Implementa l'operazione `request` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ValueError`, `VaultInitRequest`, `_`, `self.path_edit.text`, `self.privacy_combo.currentData`, `self.recipient_combo.currentData`, `self.require_signature.isChecked`, `self.signer_combo.currentData`, `str`, `strip`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog -->
#### `main.SettingsDialog`

**Tipo:** classe  
**Righe:** 1172-1337  
**Basi:** `QDialog`  
**Metodi:** `__init__`, `_lines`, `_verify_gnupg`, `apply`  
**Responsabilità:** Edit the global Keys NG config.toml without exposing TOML syntax.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog.__init__ -->
#### `main.SettingsDialog.__init__`

**Tipo:** funzione/metodo  
**Righe:** 1175-1298  
**Firma:** `def __init__(self, app_settings: AppSettings, parent=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QComboBox`, `QDialogButtonBox`, `QDoubleSpinBox`, `QFormLayout`, `QLabel`, `QLineEdit`, `QPushButton`, `QSpinBox`, `QTabWidget`, `QTextEdit`, `QVBoxLayout`, `QWidget`, `_`, `__init__`, `buttons.accepted.connect`, `buttons.rejected.connect`, `clipboard_form.addRow`, `general_form.addRow`, `help_label`, `join`, `label.setStyleSheet`, `label.setWordWrap`, `layout.addWidget`, `max`, `rdp_form.addRow`, `self.auto_lock_spin.setRange`, `self.auto_lock_spin.setSuffix`, `self.auto_lock_spin.setValue`, `self.crypto_combo.addItem`, `self.crypto_combo.findData`, `self.crypto_combo.setCurrentIndex`, `self.gpg_path_edit.setPlaceholderText`, `self.gpgconf_path_edit.setPlaceholderText`, `self.language_combo.addItem`, `self.language_combo.findData`, `self.language_combo.setCurrentIndex`, `self.password_timeout_spin.setRange`, `self.password_timeout_spin.setSuffix`, `self.password_timeout_spin.setValue`, `self.rdp_linux_options_edit.setMaximumHeight`, `self.rdp_linux_options_edit.setPlainText`, `self.rdp_macos_options_edit.setMaximumHeight`, `self.rdp_macos_options_edit.setPlainText`, `self.rdp_windows_options_edit.setMaximumHeight`, `self.rdp_windows_options_edit.setPlainText`, `self.resize`, `self.setWindowTitle`, `self.ssh_options_edit.setMaximumHeight`, `self.ssh_options_edit.setPlainText`, `self.totp_timeout_spin.setRange`, `self.totp_timeout_spin.setSuffix`, `self.totp_timeout_spin.setValue`, `self.tree_combo.addItem`, `self.tree_combo.findData`, `self.tree_combo.setCurrentIndex`, `self.tui_notice_background_edit.setPlaceholderText`, `self.tui_notice_foreground_edit.setPlaceholderText`, `self.tui_notice_seconds_spin.setRange`, `self.tui_notice_seconds_spin.setSingleStep`, `self.tui_notice_seconds_spin.setSuffix`, `self.tui_notice_seconds_spin.setValue`, `ssh_form.addRow`, `super`, `tabs.addTab`, `verify_gpg.clicked.connect`.

**Attributi oggetto modificati:** `self.app_settings`, `self.auto_lock_spin`, `self.crypto_combo`, `self.gpg_path_edit`, `self.gpgconf_path_edit`, `self.language_combo`, `self.password_timeout_spin`, `self.rdp_linux_client_edit`, `self.rdp_linux_options_edit`, `self.rdp_macos_client_edit`, `self.rdp_macos_options_edit`, `self.rdp_windows_client_edit`, `self.rdp_windows_options_edit`, `self.ssh_options_edit`, `self.ssh_terminal_edit`, `self.totp_timeout_spin`, `self.tree_combo`, `self.tui_notice_background_edit`, `self.tui_notice_foreground_edit`, `self.tui_notice_seconds_spin`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog.__init__.help_label -->
#### `main.SettingsDialog.__init__.help_label`

**Tipo:** funzione/metodo  
**Righe:** 1184-1188  
**Firma:** `def help_label(text: str) -> QLabel`  
**Scopo:** Implementa l'operazione `help_label` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QLabel`, `label.setStyleSheet`, `label.setWordWrap`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog._lines -->
#### `main.SettingsDialog._lines`

**Tipo:** funzione/metodo  
**Righe:** 1301-1302  
**Firma:** `def _lines(widget: QTextEdit) -> list[str]`  
**Scopo:** Helper interno che implementa `_lines`.

**Chiamate dirette osservate nel corpo:** `line.strip`, `splitlines`, `widget.toPlainText`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog._verify_gnupg -->
#### `main.SettingsDialog._verify_gnupg`

**Tipo:** funzione/metodo  
**Righe:** 1304-1314  
**Firma:** `def _verify_gnupg(self) -> None`  
**Scopo:** Helper interno che implementa `_verify_gnupg`.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `QMessageBox.information`, `_`, `backend.diagnose`, `create_crypto_backend`, `join`, `self.gpg_path_edit.text`, `self.gpgconf_path_edit.text`, `str`, `strip`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.SettingsDialog.apply -->
#### `main.SettingsDialog.apply`

**Tipo:** funzione/metodo  
**Righe:** 1316-1337  
**Firma:** `def apply(self) -> None`  
**Scopo:** Implementa l'operazione `apply` in questo modulo.

**Chiamate dirette osservate nel corpo:** `float`, `s.save`, `self._lines`, `self.auto_lock_spin.value`, `self.crypto_combo.currentData`, `self.gpg_path_edit.text`, `self.gpgconf_path_edit.text`, `self.language_combo.currentData`, `self.password_timeout_spin.value`, `self.rdp_linux_client_edit.text`, `self.rdp_macos_client_edit.text`, `self.rdp_windows_client_edit.text`, `self.ssh_terminal_edit.text`, `self.totp_timeout_spin.value`, `self.tree_combo.currentData`, `self.tui_notice_background_edit.text`, `self.tui_notice_foreground_edit.text`, `self.tui_notice_seconds_spin.value`, `str`, `strip`.

**Attributi oggetto modificati:** `s.auto_lock_timeout`, `s.clipboard_password_timeout`, `s.clipboard_totp_timeout`, `s.crypto_backend`, `s.gpg_executable`, `s.gpgconf_executable`, `s.language`, `s.rdp_linux_client`, `s.rdp_linux_options`, `s.rdp_macos_client`, `s.rdp_macos_options`, `s.rdp_windows_client`, `s.rdp_windows_options`, `s.ssh_terminal`, `s.ssh_terminal_options`, `s.tree_startup_view`, `s.tui_clipboard_notice_background`, `s.tui_clipboard_notice_foreground`, `s.tui_clipboard_notice_seconds`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow -->
#### `main.MainWindow`

**Tipo:** classe  
**Righe:** 1339-1624  
**Basi:** `QMainWindow`  
**Metodi:** `__init__`, `_menu_action`, `build_menus`, `copy_context_or_password`, `show_keepassxc_import`, `export_vault_keepassxc`, `show_inbox`, `show_trusted_signers`, `show_preferences`, `refresh_recent_menu`, `show_help`, `active_pane`, `call_active`, `_sync_empty_state`, `update_window_title`, `create_vault_wizard`, `open_vault_dialog`, `open_vault`, `close_current_vault`, `close_vault`, `hard_lock_all`  
**Responsabilità:** Finestra GUI principale che coordina più istanze VaultPane.

<!-- symbol:keys_ng.gui.main:main.MainWindow.__init__ -->
#### `main.MainWindow.__init__`

**Tipo:** funzione/metodo  
**Righe:** 1340-1395  
**Firma:** `def __init__(self, initial_vaults: list[str]) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `QKeySequence`, `QLabel`, `QPushButton`, `QShortcut`, `QStackedWidget`, `QTabWidget`, `QVBoxLayout`, `QWidget`, `_`, `__init__`, `create_button.clicked.connect`, `empty_label.setAlignment`, `empty_layout.addStretch`, `empty_layout.addWidget`, `open_button.clicked.connect`, `self._sync_empty_state`, `self.build_menus`, `self.call_active`, `self.open_vault`, `self.setCentralWidget`, `self.setWindowTitle`, `self.shortcuts.append`, `self.stack.addWidget`, `self.tabs.currentChanged.connect`, `self.tabs.setMovable`, `self.tabs.setTabPosition`, `self.tabs.setTabsClosable`, `self.tabs.tabCloseRequested.connect`, `shortcut.activated.connect`, `shortcut.setContext`, `super`.

**Attributi oggetto modificati:** `self.empty_page`, `self.shortcuts`, `self.stack`, `self.tabs`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow._menu_action -->
#### `main.MainWindow._menu_action`

**Tipo:** funzione/metodo  
**Righe:** 1397-1401  
**Firma:** `def _menu_action(self, menu, label: str, callback, shortcut_text: str | None=None)`  
**Scopo:** Helper interno che implementa `_menu_action`.

**Chiamate dirette osservate nel corpo:** `action.triggered.connect`, `menu.addAction`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.build_menus -->
#### `main.MainWindow.build_menus`

**Tipo:** funzione/metodo  
**Righe:** 1403-1450  
**Firma:** `def build_menus(self) -> None`  
**Scopo:** Costruisce `build_menus`.

**Chiamate dirette osservate nel corpo:** `_`, `addMenu`, `entry_menu.addSeparator`, `preferences_action.setMenuRole`, `self._menu_action`, `self.call_active`, `self.menuBar`, `self.recent_menu.aboutToShow.connect`, `self.refresh_recent_menu`, `self.show_help`, `vault_menu.addMenu`, `vault_menu.addSeparator`.

**Attributi oggetto modificati:** `self.recent_menu`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.copy_context_or_password -->
#### `main.MainWindow.copy_context_or_password`

**Tipo:** funzione/metodo  
**Righe:** 1452-1458  
**Firma:** `def copy_context_or_password(self) -> None`  
**Scopo:** Copia un valore usando `copy_context_or_password`.

**Chiamate dirette osservate nel corpo:** `QApplication.focusWidget`, `focus.copy`, `focus.hasSelectedText`, `focus.textCursor`, `hasSelection`, `isinstance`, `self.call_active`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_keepassxc_import -->
#### `main.MainWindow.show_keepassxc_import`

**Tipo:** funzione/metodo  
**Righe:** 1460-1466  
**Firma:** `def show_keepassxc_import(self) -> None`  
**Scopo:** Implementa l'operazione `show_keepassxc_import` in questo modulo.

**Chiamate dirette osservate nel corpo:** `KeePassXCImportDialog`, `_`, `dialog.exec`, `pane.reload`, `self.active_pane`, `self.statusBar`, `showMessage`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.export_vault_keepassxc -->
#### `main.MainWindow.export_vault_keepassxc`

**Tipo:** funzione/metodo  
**Righe:** 1468-1479  
**Firma:** `def export_vault_keepassxc(self) -> None`  
**Scopo:** Esporta `export_vault_keepassxc`.

**Chiamate dirette osservate nel corpo:** `QFileDialog.getSaveFileName`, `QMessageBox.critical`, `QMessageBox.warning`, `_`, `export_vault_xml`, `self.active_pane`, `self.statusBar`, `showMessage`, `str`, `write_export`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_inbox -->
#### `main.MainWindow.show_inbox`

**Tipo:** funzione/metodo  
**Righe:** 1481-1485  
**Firma:** `def show_inbox(self) -> None`  
**Scopo:** Implementa l'operazione `show_inbox` in questo modulo.

**Chiamate dirette osservate nel corpo:** `InboxDialog`, `exec`, `pane.reload`, `self.active_pane`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_trusted_signers -->
#### `main.MainWindow.show_trusted_signers`

**Tipo:** funzione/metodo  
**Righe:** 1487-1490  
**Firma:** `def show_trusted_signers(self) -> None`  
**Scopo:** Implementa l'operazione `show_trusted_signers` in questo modulo.

**Chiamate dirette osservate nel corpo:** `TrustedSignersDialog`, `exec`, `self.active_pane`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_preferences -->
#### `main.MainWindow.show_preferences`

**Tipo:** funzione/metodo  
**Righe:** 1492-1504  
**Firma:** `def show_preferences(self) -> None`  
**Scopo:** Implementa l'operazione `show_preferences` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QMessageBox.critical`, `SettingsDialog`, `_`, `dialog.apply`, `dialog.exec`, `isinstance`, `pane.reset_auto_lock_timer`, `range`, `self.statusBar`, `self.tabs.count`, `self.tabs.widget`, `showMessage`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.refresh_recent_menu -->
#### `main.MainWindow.refresh_recent_menu`

**Tipo:** funzione/metodo  
**Righe:** 1506-1518  
**Firma:** `def refresh_recent_menu(self) -> None`  
**Scopo:** Implementa l'operazione `refresh_recent_menu` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path`, `_`, `action.setEnabled`, `action.setToolTip`, `action.triggered.connect`, `list`, `self.open_vault`, `self.recent_menu.addAction`, `self.recent_menu.clear`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.show_help -->
#### `main.MainWindow.show_help`

**Tipo:** funzione/metodo  
**Righe:** 1520-1521  
**Firma:** `def show_help(self, tab: int=0) -> None`  
**Scopo:** Implementa l'operazione `show_help` in questo modulo.

**Chiamate dirette osservate nel corpo:** `HelpDialog`, `exec`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.active_pane -->
#### `main.MainWindow.active_pane`

**Tipo:** funzione/metodo  
**Righe:** 1523-1525  
**Firma:** `def active_pane(self) -> VaultPane | None`  
**Scopo:** Implementa l'operazione `active_pane` in questo modulo.

**Chiamate dirette osservate nel corpo:** `isinstance`, `self.tabs.currentWidget`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.call_active -->
#### `main.MainWindow.call_active`

**Tipo:** funzione/metodo  
**Righe:** 1527-1531  
**Firma:** `def call_active(self, method: str, *args) -> None`  
**Scopo:** Implementa l'operazione `call_active` in questo modulo.

**Chiamate dirette osservate nel corpo:** `getattr`, `self.active_pane`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow._sync_empty_state -->
#### `main.MainWindow._sync_empty_state`

**Tipo:** funzione/metodo  
**Righe:** 1533-1535  
**Firma:** `def _sync_empty_state(self) -> None`  
**Scopo:** Helper interno che implementa `_sync_empty_state`.

**Chiamate dirette osservate nel corpo:** `self.stack.setCurrentWidget`, `self.tabs.count`, `self.update_window_title`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.update_window_title -->
#### `main.MainWindow.update_window_title`

**Tipo:** funzione/metodo  
**Righe:** 1537-1539  
**Firma:** `def update_window_title(self, _index: int | None=None) -> None`  
**Scopo:** Implementa l'operazione `update_window_title` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.active_pane`, `self.setWindowTitle`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.create_vault_wizard -->
#### `main.MainWindow.create_vault_wizard`

**Tipo:** funzione/metodo  
**Righe:** 1541-1553  
**Firma:** `def create_vault_wizard(self) -> None`  
**Scopo:** Crea `create_vault_wizard`.

**Chiamate dirette osservate nel corpo:** `NewVaultWizard`, `QMessageBox.critical`, `_`, `create_crypto_backend`, `create_vault`, `self.open_vault`, `self.statusBar`, `showMessage`, `str`, `wizard.exec`, `wizard.request`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.open_vault_dialog -->
#### `main.MainWindow.open_vault_dialog`

**Tipo:** funzione/metodo  
**Righe:** 1555-1558  
**Firma:** `def open_vault_dialog(self) -> None`  
**Scopo:** Implementa l'operazione `open_vault_dialog` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path.home`, `QFileDialog.getExistingDirectory`, `_`, `self.open_vault`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.open_vault -->
#### `main.MainWindow.open_vault`

**Tipo:** funzione/metodo  
**Righe:** 1560-1591  
**Firma:** `def open_vault(self, path: str) -> None`  
**Scopo:** Implementa l'operazione `open_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path`, `QMessageBox.critical`, `QMessageBox.information`, `VaultPane`, `_`, `expanduser`, `format`, `isinstance`, `len`, `pending_inbox_paths`, `range`, `resolve`, `self._sync_empty_state`, `self.refresh_recent_menu`, `self.show_inbox`, `self.tabs.addTab`, `self.tabs.count`, `self.tabs.setCurrentIndex`, `self.tabs.setTabToolTip`, `self.tabs.widget`, `settings.remember_vault`, `settings.save`, `str`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 1 cicli, 2 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.close_current_vault -->
#### `main.MainWindow.close_current_vault`

**Tipo:** funzione/metodo  
**Righe:** 1593-1596  
**Firma:** `def close_current_vault(self) -> None`  
**Scopo:** Implementa l'operazione `close_current_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.close_vault`, `self.tabs.currentIndex`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.close_vault -->
#### `main.MainWindow.close_vault`

**Tipo:** funzione/metodo  
**Righe:** 1598-1609  
**Firma:** `def close_vault(self, index: int) -> None`  
**Scopo:** Implementa l'operazione `close_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `isinstance`, `pane.clear_details`, `pane.deleteLater`, `pane.vault.lock`, `self._sync_empty_state`, `self.tabs.removeTab`, `self.tabs.widget`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.gui.main:main.MainWindow.hard_lock_all -->
#### `main.MainWindow.hard_lock_all`

**Tipo:** funzione/metodo  
**Righe:** 1611-1624  
**Firma:** `def hard_lock_all(self) -> None`  
**Scopo:** Implementa l'operazione `hard_lock_all` in questo modulo.

**Chiamate dirette osservate nel corpo:** `QApplication.clipboard`, `QMessageBox.critical`, `_`, `clear`, `isinstance`, `pane.clear_details`, `pane.vault.lock`, `range`, `self.statusBar`, `self.tabs.count`, `self.tabs.widget`, `showMessage`, `str`, `vault.crypto.hard_lock`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent, clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.i18n.manager`

Rilevamento lingua gettext e helper di traduzione.

**Sorgente:** `src/keys_ng/i18n/manager.py`  
**Simboli eseguibili:** 7

**Dipendenze dirette del modulo:** `__future__`, `gettext`, `locale`, `pathlib`

<!-- symbol:keys_ng.i18n.manager:_locales_dir -->
#### `_locales_dir`

**Tipo:** funzione/metodo  
**Righe:** 12-23  
**Firma:** `def _locales_dir() -> Path`  
**Scopo:** Helper interno che implementa `_locales_dir`.

**Chiamate dirette osservate nel corpo:** `Path`, `bundled.exists`, `candidate.exists`, `resolve`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.i18n.manager:_language_code -->
#### `_language_code`

**Tipo:** funzione/metodo  
**Righe:** 26-29  
**Firma:** `def _language_code(value: str | None) -> str`  
**Scopo:** Helper interno che implementa `_language_code`.

**Chiamate dirette osservate nel corpo:** `lower`, `split`, `value.replace`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.i18n.manager:configure_language -->
#### `configure_language`

**Tipo:** funzione/metodo  
**Righe:** 32-42  
**Firma:** `def configure_language(language: str | None=None) -> None`  
**Scopo:** Implementa l'operazione `configure_language` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_language_code`, `_locales_dir`, `gettext.translation`, `locale.getlocale`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.i18n.manager:current_language -->
#### `current_language`

**Tipo:** funzione/metodo  
**Righe:** 45-46  
**Firma:** `def current_language() -> str`  
**Scopo:** Implementa l'operazione `current_language` in questo modulo.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.i18n.manager:_ -->
#### `_`

**Tipo:** funzione/metodo  
**Righe:** 49-50  
**Firma:** `def _(message: str) -> str`  
**Scopo:** Helper interno che implementa `_`.

**Chiamate dirette osservate nel corpo:** `_translation.gettext`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.i18n.manager:ngettext -->
#### `ngettext`

**Tipo:** funzione/metodo  
**Righe:** 53-54  
**Firma:** `def ngettext(singular: str, plural: str, n: int) -> str`  
**Scopo:** Implementa l'operazione `ngettext` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_translation.ngettext`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.i18n.manager:pgettext -->
#### `pgettext`

**Tipo:** funzione/metodo  
**Righe:** 57-59  
**Firma:** `def pgettext(context: str, message: str) -> str`  
**Scopo:** Implementa l'operazione `pgettext` in questo modulo.

**Chiamate dirette osservate nel corpo:** `fn`, `getattr`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.migration.keepassxc`

Import XML/KDBX KeePassXC, mappatura UUID e validazione sicura dei riferimenti.

**Sorgente:** `src/keys_ng/migration/keepassxc.py`  
**Simboli eseguibili:** 24

**Dipendenze dirette del modulo:** `__future__`, `base64`, `binascii`, `dataclasses`, `keys_ng.errors`, `keys_ng.models`, `keys_ng.services.references`, `keys_ng.services.totp`, `keys_ng.storage.vault`, `os`, `pathlib`, `re`, `shutil`, `subprocess`, `sys`, `urllib.parse`, `uuid`, `xml.etree.ElementTree`

<!-- symbol:keys_ng.migration.keepassxc:KeePassXCImportReport -->
#### `KeePassXCImportReport`

**Tipo:** classe  
**Righe:** 44-56  
**Campi dichiarati:** `entries`, `folders`, `totp_tokens`, `custom_fields`, `skipped_recycle_bin`, `uuid_preserved`, `uuid_remapped`, `uuid_generated`, `references_found`, `references_remapped`, `references_validated`, `warnings`  
**Responsabilità:** Implementa l'operazione `KeePassXCImportReport` in questo modulo.

<!-- symbol:keys_ng.migration.keepassxc:_PendingEntry -->
#### `_PendingEntry`

**Tipo:** classe  
**Righe:** 60-63  
**Campi dichiarati:** `entry`, `folder_path`, `source_uuid`  
**Responsabilità:** Helper interno che implementa `_PendingEntry`.

<!-- symbol:keys_ng.migration.keepassxc:_safe_xml_root -->
#### `_safe_xml_root`

**Tipo:** funzione/metodo  
**Righe:** 66-75  
**Firma:** `def _safe_xml_root(raw: bytes) -> ET.Element`  
**Scopo:** Helper interno che implementa `_safe_xml_root`.

**Chiamate dirette osservate nel corpo:** `ET.fromstring`, `ValueError`, `len`, `upper`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_text -->
#### `_text`

**Tipo:** funzione/metodo  
**Righe:** 78-80  
**Firma:** `def _text(parent: ET.Element, path: str, default: str='') -> str`  
**Scopo:** Helper interno che implementa `_text`.

**Chiamate dirette osservate nel corpo:** `parent.find`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_strings -->
#### `_strings`

**Tipo:** funzione/metodo  
**Righe:** 83-90  
**Firma:** `def _strings(entry_node: ET.Element) -> dict[str, str]`  
**Scopo:** Helper interno che implementa `_strings`.

**Chiamate dirette osservate nel corpo:** `_text`, `entry_node.findall`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_decode_keepass_uuid -->
#### `_decode_keepass_uuid`

**Tipo:** funzione/metodo  
**Righe:** 93-113  
**Firma:** `def _decode_keepass_uuid(value: str) -> str | None`  
**Scopo:** Convert a KeePass XML UUID to Keys NG's canonical RFC-4122 form. KDBX XML serializes UUID elements as base64Binary containing 16 UUID bytes. For robustness, canonical/32-hex UUID strings are accepted too; this is useful with hand-written exports and tests, but real KeePassXC XML normally uses Base64.

**Chiamate dirette osservate nel corpo:** `ValueError`, `base64.b64decode`, `len`, `str`, `uuid.UUID`, `value.strip`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_uuid_compare_key -->
#### `_uuid_compare_key`

**Tipo:** funzione/metodo  
**Righe:** 116-124  
**Firma:** `def _uuid_compare_key(value: str) -> str`  
**Scopo:** Normalize UUIDs when possible, otherwise preserve opaque legacy test IDs.

**Chiamate dirette osservate nel corpo:** `_decode_keepass_uuid`, `value.strip`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_normalize_totp_algorithm -->
#### `_normalize_totp_algorithm`

**Tipo:** funzione/metodo  
**Righe:** 127-131  
**Firma:** `def _normalize_totp_algorithm(value: str) -> str`  
**Scopo:** Helper interno che implementa `_normalize_totp_algorithm`.

**Chiamate dirette osservate nel corpo:** `replace`, `upper`, `value.strip`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_parse_totp -->
#### `_parse_totp`

**Tipo:** funzione/metodo  
**Righe:** 134-156  
**Firma:** `def _parse_totp(fields: dict[str, str], title: str, username: str) -> list[TotpConfig]`  
**Scopo:** Helper interno che implementa `_parse_totp`.

**Chiamate dirette osservate nel corpo:** `_normalize_totp_algorithm`, `fields.get`, `int`, `otp.lower`, `parse_otpauth_uri`, `startswith`, `strip`, `totp_from_secret`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 3 blocchi try, 0 context manager, 4 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_action_from_url -->
#### `_action_from_url`

**Tipo:** funzione/metodo  
**Righe:** 159-171  
**Firma:** `def _action_from_url(value: str, username: str) -> tuple[list[Action], str | None]`  
**Scopo:** Helper interno che implementa `_action_from_url`.

**Chiamate dirette osservate nel corpo:** `Action`, `parsed.scheme.lower`, `urlparse`, `value.strip`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 5 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_parse_tags -->
#### `_parse_tags`

**Tipo:** funzione/metodo  
**Righe:** 174-179  
**Firma:** `def _parse_tags(entry_node: ET.Element) -> list[str]`  
**Scopo:** Helper interno che implementa `_parse_tags`.

**Chiamate dirette osservate nel corpo:** `_text`, `part.strip`, `raw.split`, `strip`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_entry_from_xml -->
#### `_entry_from_xml`

**Tipo:** funzione/metodo  
**Righe:** 182-214  
**Firma:** `def _entry_from_xml(entry_node: ET.Element, report: KeePassXCImportReport) -> Entry`  
**Scopo:** Helper interno che implementa `_entry_from_xml`.

**Chiamate dirette osservate nel corpo:** `Entry.create`, `_action_from_url`, `_parse_tags`, `_parse_totp`, `_strings`, `custom.setdefault`, `fields.get`, `fields.items`, `len`, `strip`.

**Attributi oggetto modificati:** `report.custom_fields`, `report.totp_tokens`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_new_unique_uuid -->
#### `_new_unique_uuid`

**Tipo:** funzione/metodo  
**Righe:** 217-222  
**Firma:** `def _new_unique_uuid(reserved: set[str]) -> str`  
**Scopo:** Helper interno che implementa `_new_unique_uuid`.

**Chiamate dirette osservate nel corpo:** `reserved.add`, `str`, `uuid.uuid4`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_rewrite_reference_text -->
#### `_rewrite_reference_text`

**Tipo:** funzione/metodo  
**Righe:** 225-241  
**Firma:** `def _rewrite_reference_text(value: str | None, uuid_map: dict[str, str], report: KeePassXCImportReport) -> str | None`  
**Scopo:** Helper interno che implementa `_rewrite_reference_text`.

**Chiamate dirette osservate nel corpo:** `_UUID_REFERENCE_RE.sub`, `field_name.upper`, `match.group`, `match.groups`, `normalize_entry_uuid`, `uuid_map.get`, `value.upper`.

**Attributi oggetto modificati:** `report.references_found`, `report.references_remapped`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 4 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_rewrite_reference_text.replace -->
#### `_rewrite_reference_text.replace`

**Tipo:** funzione/metodo  
**Righe:** 229-239  
**Firma:** `def replace(match: re.Match[str]) -> str`  
**Scopo:** Implementa l'operazione `replace` in questo modulo.

**Chiamate dirette osservate nel corpo:** `field_name.upper`, `match.group`, `match.groups`, `normalize_entry_uuid`, `uuid_map.get`.

**Attributi oggetto modificati:** `report.references_found`, `report.references_remapped`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_rewrite_entry_references -->
#### `_rewrite_entry_references`

**Tipo:** funzione/metodo  
**Righe:** 244-257  
**Firma:** `def _rewrite_entry_references(entry: Entry, uuid_map: dict[str, str], report: KeePassXCImportReport) -> None`  
**Scopo:** Helper interno che implementa `_rewrite_entry_references`.

**Chiamate dirette osservate nel corpo:** `_rewrite_reference_text`, `entry.custom_fields.items`.

**Attributi oggetto modificati:** `action.argv`, `action.ssh_options`, `action.url`, `action.username`, `entry.custom_fields`, `entry.notes`, `entry.password`, `entry.title`, `entry.usernames`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_validate_import_references -->
#### `_validate_import_references`

**Tipo:** funzione/metodo  
**Righe:** 260-295  
**Firma:** `def _validate_import_references(pending: list[_PendingEntry], vault: Vault, report: KeePassXCImportReport) -> None`  
**Scopo:** Resolve every whole-field imported U/P reference before any record is saved.

**Chiamate dirette osservate nel corpo:** `ValueError`, `checked.add`, `join`, `len`, `load_entry`, `parse_entry_reference`, `resolve`, `set`, `vault.get_entry`, `vault.list_items`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Attributi oggetto modificati:** `report.references_validated`.

**Forma del flusso di controllo:** 6 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 4 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_validate_import_references.load_entry -->
#### `_validate_import_references.load_entry`

**Tipo:** funzione/metodo  
**Righe:** 266-271  
**Firma:** `def load_entry(entry_id: str) -> Entry`  
**Scopo:** Carica e valida `load_entry`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `vault.get_entry`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:_validate_import_references.resolve -->
#### `_validate_import_references.resolve`

**Tipo:** funzione/metodo  
**Righe:** 273-286  
**Firma:** `def resolve(value: str | None, stack: tuple[tuple[str, str], ...]=()) -> str | None`  
**Scopo:** Implementa l'operazione `resolve` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ValueError`, `checked.add`, `join`, `load_entry`, `parse_entry_reference`, `resolve`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:import_keepassxc_xml -->
#### `import_keepassxc_xml`

**Tipo:** funzione/metodo  
**Righe:** 298-406  
**Firma:** `def import_keepassxc_xml(raw: bytes, vault: Vault, *, dry_run: bool=False) -> KeePassXCImportReport`  
**Scopo:** Import KeePassXC XML using UUID-preserving, reference-safe two-pass migration. Pass 1 collects the entire source tree and source UUIDs. Pass 2 assigns target UUIDs, rewrites all UUID references, validates whole-field U/P reference chains, and only then writes folders/entries to the destination vault.

**Chiamate dirette osservate nel corpo:** `KeePassXCImportReport`, `ValueError`, `_PendingEntry`, `_decode_keepass_uuid`, `_entry_from_xml`, `_new_unique_uuid`, `_rewrite_entry_references`, `_safe_xml_root`, `_text`, `_uuid_compare_key`, `_validate_import_references`, `collect_group`, `group_node.findall`, `parse_entry_reference`, `pending.append`, `report.warnings.append`, `reserved.add`, `root.find`, `set`, `source_seen.add`, `strip`, `vault.create_folder_path`, `vault.get_entry`, `vault.list_items`, `vault.resolved_action`, `vault.resolved_password`, `vault.resolved_username`, `vault.save_entry`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Attributi oggetto modificati:** `item.entry.folder_id`, `item.entry.id`, `report.entries`, `report.folders`, `report.skipped_recycle_bin`, `report.uuid_generated`, `report.uuid_preserved`, `report.uuid_remapped`.

**Forma del flusso di controllo:** 15 blocchi condizionali, 7 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:import_keepassxc_xml.collect_group -->
#### `import_keepassxc_xml.collect_group`

**Tipo:** funzione/metodo  
**Righe:** 318-343  
**Firma:** `def collect_group(group_node: ET.Element, parent_path: str, create_folder: bool) -> None`  
**Scopo:** Implementa l'operazione `collect_group` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ValueError`, `_PendingEntry`, `_decode_keepass_uuid`, `_entry_from_xml`, `_text`, `_uuid_compare_key`, `collect_group`, `group_node.findall`, `pending.append`, `source_seen.add`, `strip`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Attributi oggetto modificati:** `report.entries`, `report.folders`, `report.skipped_recycle_bin`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:export_kdbx_to_xml -->
#### `export_kdbx_to_xml`

**Tipo:** funzione/metodo  
**Righe:** 409-454  
**Firma:** `def export_kdbx_to_xml(database: str | Path, *, key_file: str | Path | None=None, no_password: bool=False, yubikey: str | None=None, keepassxc_cli: str | None=None, password: str | None=None) -> bytes`  
**Scopo:** Esporta `export_kdbx_to_xml`.

**Chiamate dirette osservate nel corpo:** `Path`, `RuntimeError`, `argv.append`, `argv.extend`, `candidates.append`, `encode`, `expanduser`, `next`, `os.environ.get`, `path.is_file`, `process.communicate`, `str`, `subprocess.Popen`, `which`.

**Eccezioni sollevate esplicitamente:** `RuntimeError`.

**Forma del flusso di controllo:** 11 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:import_keepassxc -->
#### `import_keepassxc`

**Tipo:** funzione/metodo  
**Righe:** 457-478  
**Firma:** `def import_keepassxc(source: str | Path, vault: Vault, *, source_format: str='auto', key_file: str | Path | None=None, no_password: bool=False, yubikey: str | None=None, dry_run: bool=False, password: str | None=None) -> KeePassXCImportReport`  
**Scopo:** Importa `import_keepassxc`.

**Chiamate dirette osservate nel corpo:** `Path`, `ValueError`, `expanduser`, `export_kdbx_to_xml`, `import_keepassxc_xml`, `path.read_bytes`, `path.suffix.lower`, `source_format.lower`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc:format_import_report -->
#### `format_import_report`

**Tipo:** funzione/metodo  
**Righe:** 481-496  
**Firma:** `def format_import_report(report: KeePassXCImportReport) -> str`  
**Scopo:** Render a concise, frontend-neutral KeePassXC import summary.

**Chiamate dirette osservate nel corpo:** `join`, `lines.append`, `lines.extend`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.migration.keepassxc_export`

Esportazione XML compatibile KeePass per una voce o per l'intero vault.

**Sorgente:** `src/keys_ng/migration/keepassxc_export.py`  
**Simboli eseguibili:** 11

**Dipendenze dirette del modulo:** `__future__`, `base64`, `keys_ng.models`, `keys_ng.services.references`, `keys_ng.services.ssh_options`, `keys_ng.services.totp`, `keys_ng.storage.vault`, `pathlib`, `re`, `uuid`, `xml.etree.ElementTree`

<!-- symbol:keys_ng.migration.keepassxc_export:_keepass_uuid -->
#### `_keepass_uuid`

**Tipo:** funzione/metodo  
**Righe:** 18-20  
**Firma:** `def _keepass_uuid(value: str) -> str`  
**Scopo:** Encode an RFC-4122 UUID as KeePass XML's base64Binary UUID.

**Chiamate dirette osservate nel corpo:** `base64.b64encode`, `decode`, `uuid.UUID`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:_reference_to_keepass -->
#### `_reference_to_keepass`

**Tipo:** funzione/metodo  
**Righe:** 23-32  
**Firma:** `def _reference_to_keepass(value: str | None) -> str`  
**Scopo:** Helper interno che implementa `_reference_to_keepass`.

**Chiamate dirette osservate nel corpo:** `_REF_RE.sub`, `canonical.hex.upper`, `field.upper`, `match.groups`, `uuid.UUID`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:_reference_to_keepass.repl -->
#### `_reference_to_keepass.repl`

**Tipo:** funzione/metodo  
**Righe:** 27-30  
**Firma:** `def repl(match: re.Match[str]) -> str`  
**Scopo:** Implementa l'operazione `repl` in questo modulo.

**Chiamate dirette osservate nel corpo:** `canonical.hex.upper`, `field.upper`, `match.groups`, `uuid.UUID`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:_add_string -->
#### `_add_string`

**Tipo:** funzione/metodo  
**Righe:** 35-41  
**Firma:** `def _add_string(parent: ET.Element, key: str, value: str, *, protected: bool=False) -> None`  
**Scopo:** Helper interno che implementa `_add_string`.

**Chiamate dirette osservate nel corpo:** `ET.SubElement`, `value_node.set`.

**Attributi oggetto modificati:** `text`, `value_node.text`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:_action_url -->
#### `_action_url`

**Tipo:** funzione/metodo  
**Righe:** 44-53  
**Firma:** `def _action_url(action: Action | None) -> str`  
**Scopo:** Helper interno che implementa `_action_url`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 4 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:_entry_xml -->
#### `_entry_xml`

**Tipo:** funzione/metodo  
**Righe:** 56-100  
**Firma:** `def _entry_xml(entry: Entry, vault: Vault, *, resolve_references: bool) -> ET.Element`  
**Scopo:** Helper interno che implementa `_entry_xml`.

**Chiamate dirette osservate nel corpo:** `ET.Element`, `ET.SubElement`, `_action_url`, `_add_string`, `_keepass_uuid`, `_reference_to_keepass`, `build_otpauth_uri`, `entry.custom_fields.items`, `format_ssh_options`, `join`, `sorted`, `vault.resolved_password`, `vault.resolved_username`.

**Attributi oggetto modificati:** `text`.

**Forma del flusso di controllo:** 10 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:_new_group -->
#### `_new_group`

**Tipo:** funzione/metodo  
**Righe:** 103-108  
**Firma:** `def _new_group(name: str, group_id: str | None=None) -> ET.Element`  
**Scopo:** Helper interno che implementa `_new_group`.

**Chiamate dirette osservate nel corpo:** `ET.Element`, `ET.SubElement`, `_keepass_uuid`, `str`, `uuid.uuid4`.

**Attributi oggetto modificati:** `text`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:_document -->
#### `_document`

**Tipo:** funzione/metodo  
**Righe:** 111-121  
**Firma:** `def _document(root_group: ET.Element, database_name: str) -> bytes`  
**Scopo:** Helper interno che implementa `_document`.

**Chiamate dirette osservate nel corpo:** `ET.Element`, `ET.SubElement`, `ET.indent`, `ET.tostring`, `root_node.append`.

**Attributi oggetto modificati:** `text`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:export_entry_xml -->
#### `export_entry_xml`

**Tipo:** funzione/metodo  
**Righe:** 124-133  
**Firma:** `def export_entry_xml(vault: Vault, entry_id: str) -> bytes`  
**Scopo:** Export one entry as a standalone KeePass/KeePassXC XML document. Credential references are resolved because their target entries are not part of a single-entry export.

**Chiamate dirette osservate nel corpo:** `_document`, `_entry_xml`, `_new_group`, `group.append`, `vault.get_entry`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:export_vault_xml -->
#### `export_vault_xml`

**Tipo:** funzione/metodo  
**Righe:** 136-164  
**Firma:** `def export_vault_xml(vault: Vault) -> bytes`  
**Scopo:** Export the complete vault hierarchy as KeePass/KeePassXC XML. Entry UUIDs are preserved, so Keys NG UUID references can be translated to KeePassXC UUID-reference syntax without resolving shared credentials.

**Chiamate dirette osservate nel corpo:** `ValueError`, `_document`, `_entry_xml`, `_new_group`, `group_by_id.get`, `list`, `parent.append`, `remaining.remove`, `vault.get_entry`, `vault.list_folders`, `vault.list_items`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 3 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.keepassxc_export:write_export -->
#### `write_export`

**Tipo:** funzione/metodo  
**Righe:** 167-176  
**Firma:** `def write_export(path: str | Path, raw: bytes) -> Path`  
**Scopo:** Write a plaintext XML export with restrictive permissions where possible.

**Chiamate dirette osservate nel corpo:** `Path`, `destination.parent.mkdir`, `destination.write_bytes`, `expanduser`, `os.chmod`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.migration.legacy_parser`

Parser non esecutivo per la sintassi dei record Bash legacy.

**Sorgente:** `src/keys_ng/migration/legacy_parser.py`  
**Simboli eseguibili:** 2

**Dipendenze dirette del modulo:** `__future__`, `keys_ng.errors`, `re`

<!-- symbol:keys_ng.migration.legacy_parser:_unescape_single_quoted_legacy -->
#### `_unescape_single_quoted_legacy`

**Tipo:** funzione/metodo  
**Righe:** 11-25  
**Firma:** `def _unescape_single_quoted_legacy(value: str) -> str`  
**Scopo:** Helper interno che implementa `_unescape_single_quoted_legacy`.

**Chiamate dirette osservate nel corpo:** `LegacyFormatError`, `join`, `len`, `out.append`.

**Eccezioni sollevate esplicitamente:** `LegacyFormatError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.legacy_parser:parse_legacy_record -->
#### `parse_legacy_record`

**Tipo:** funzione/metodo  
**Righe:** 28-43  
**Firma:** `def parse_legacy_record(text: str) -> dict[str, str]`  
**Scopo:** Analizza e valida `parse_legacy_record`.

**Chiamate dirette osservate nel corpo:** `LegacyFormatError`, `_ASSIGNMENT.fullmatch`, `_unescape_single_quoted_legacy`, `enumerate`, `match.groups`, `raw.strip`, `text.splitlines`.

**Eccezioni sollevate esplicitamente:** `LegacyFormatError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.migration.migrator`

Converte un albero filesystem legacy in voci/cartelle cifrate Keys NG.

**Sorgente:** `src/keys_ng/migration/migrator.py`  
**Simboli eseguibili:** 2

**Dipendenze dirette del modulo:** `__future__`, `keys_ng.crypto.backend`, `keys_ng.migration.legacy_parser`, `keys_ng.models`, `keys_ng.storage.vault`, `pathlib`

<!-- symbol:keys_ng.migration.migrator:_legacy_kind -->
#### `_legacy_kind`

**Tipo:** funzione/metodo  
**Righe:** 11-16  
**Firma:** `def _legacy_kind(path: Path) -> tuple[str, str]`  
**Scopo:** Helper interno che implementa `_legacy_kind`.

**Chiamate dirette osservate nel corpo:** `len`, `name.endswith`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.migration.migrator:migrate_legacy_tree -->
#### `migrate_legacy_tree`

**Tipo:** funzione/metodo  
**Righe:** 19-62  
**Firma:** `def migrate_legacy_tree(source: Path, vault: Vault, crypto: CryptoBackend, dry_run: bool=False, verify: bool=False) -> list[tuple[Path, str]]`  
**Scopo:** Implementa l'operazione `migrate_legacy_tree` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Action`, `Entry.create`, `ValueError`, `_legacy_kind`, `actions.append`, `argv.append`, `crypto.decrypt`, `entry.to_bytes`, `join`, `list`, `p.is_file`, `parse_legacy_record`, `path.read_bytes`, `path.relative_to`, `plaintext.decode`, `restored.to_bytes`, `results.append`, `sorted`, `source.rglob`, `strip`, `values.get`, `vault.create_folder_path`, `vault.get_entry`, `vault.save_entry`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 7 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.models`

Modello di dominio validato in memoria e serializzabile JSON.

**Sorgente:** `src/keys_ng/models.py`  
**Simboli eseguibili:** 21

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `datetime`, `json`, `typing`, `uuid`

<!-- symbol:keys_ng.models:utc_now -->
#### `utc_now`

**Tipo:** funzione/metodo  
**Righe:** 12-13  
**Firma:** `def utc_now() -> str`  
**Scopo:** Implementa l'operazione `utc_now` in questo modulo.

**Chiamate dirette osservate nel corpo:** `datetime.now`, `isoformat`, `replace`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:TotpConfig -->
#### `TotpConfig`

**Tipo:** classe  
**Righe:** 17-33  
**Campi dichiarati:** `secret`, `issuer`, `account_name`, `algorithm`, `digits`, `period`  
**Metodi:** `validate`  
**Responsabilità:** Seed TOTP validato e parametri dell'algoritmo.

<!-- symbol:keys_ng.models:TotpConfig.validate -->
#### `TotpConfig.validate`

**Tipo:** funzione/metodo  
**Righe:** 25-33  
**Firma:** `def validate(self) -> None`  
**Scopo:** Valida gli invarianti di `validate`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `self.algorithm.upper`, `self.secret.strip`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:Action -->
#### `Action`

**Tipo:** classe  
**Righe:** 37-69  
**Campi dichiarati:** `type`, `url`, `host`, `port`, `username`, `argv`, `shell`, `ssh_x11_forwarding`, `ssh_options`  
**Metodi:** `validate`  
**Responsabilità:** Azione esterna validata associata a una voce.

<!-- symbol:keys_ng.models:Action.validate -->
#### `Action.validate`

**Tipo:** funzione/metodo  
**Righe:** 48-69  
**Firma:** `def validate(self) -> None`  
**Scopo:** Valida gli invarianti di `validate`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `all`, `isinstance`, `self.type.upper`, `validate_ssh_options`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 10 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:Folder -->
#### `Folder`

**Tipo:** classe  
**Righe:** 73-93  
**Campi dichiarati:** `id`, `name`, `parent_id`, `created_at`, `updated_at`  
**Metodi:** `create`, `validate`  
**Responsabilità:** Nodo di cartella logica identificato da UUID.

<!-- symbol:keys_ng.models:Folder.create -->
#### `Folder.create`

**Tipo:** funzione/metodo  
**Righe:** 81-82  
**Firma:** `def create(cls, name: str, parent_id: str | None=None) -> 'Folder'`  
**Scopo:** Implementa l'operazione `create` in questo modulo.

**Chiamate dirette osservate nel corpo:** `cls`, `str`, `uuid.uuid4`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:Folder.validate -->
#### `Folder.validate`

**Tipo:** funzione/metodo  
**Righe:** 84-93  
**Firma:** `def validate(self) -> None`  
**Scopo:** Valida gli invarianti di `validate`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `self.name.strip`, `uuid.UUID`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:FolderStore -->
#### `FolderStore`

**Tipo:** classe  
**Righe:** 97-129  
**Campi dichiarati:** `folders`, `schema`  
**Metodi:** `validate`, `to_bytes`, `from_bytes`  
**Responsabilità:** Albero cifrato delle cartelle logiche.

<!-- symbol:keys_ng.models:FolderStore.validate -->
#### `FolderStore.validate`

**Tipo:** funzione/metodo  
**Righe:** 101-118  
**Firma:** `def validate(self) -> None`  
**Scopo:** Valida gli invarianti di `validate`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `by_id.get`, `folder.validate`, `len`, `seen.add`, `set`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 3 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:FolderStore.to_bytes -->
#### `FolderStore.to_bytes`

**Tipo:** funzione/metodo  
**Righe:** 120-122  
**Firma:** `def to_bytes(self) -> bytes`  
**Scopo:** Serializza/converte `to_bytes`.

**Chiamate dirette osservate nel corpo:** `asdict`, `encode`, `json.dumps`, `self.validate`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:FolderStore.from_bytes -->
#### `FolderStore.from_bytes`

**Tipo:** funzione/metodo  
**Righe:** 125-129  
**Firma:** `def from_bytes(cls, raw: bytes) -> 'FolderStore'`  
**Scopo:** Deserializza/costruisce `from_bytes`.

**Chiamate dirette osservate nel corpo:** `Folder`, `cls`, `data.get`, `json.loads`, `raw.decode`, `store.validate`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:Entry -->
#### `Entry`

**Tipo:** classe  
**Righe:** 133-182  
**Campi dichiarati:** `id`, `title`, `kind`, `usernames`, `password`, `totp`, `actions`, `tags`, `notes`, `custom_fields`, `folder_id`, `revision`, `created_at`, `updated_at`, `schema`  
**Metodi:** `create`, `validate`, `to_bytes`, `from_bytes`  
**Responsabilità:** Record di credenziale persistito in un singolo file cifrato.

<!-- symbol:keys_ng.models:Entry.create -->
#### `Entry.create`

**Tipo:** funzione/metodo  
**Righe:** 151-152  
**Firma:** `def create(cls, title: str, **kwargs: Any) -> 'Entry'`  
**Scopo:** Implementa l'operazione `create` in questo modulo.

**Chiamate dirette osservate nel corpo:** `cls`, `str`, `uuid.uuid4`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:Entry.validate -->
#### `Entry.validate`

**Tipo:** funzione/metodo  
**Righe:** 154-167  
**Firma:** `def validate(self) -> None`  
**Scopo:** Valida gli invarianti di `validate`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `action.validate`, `self.title.strip`, `token.validate`, `uuid.UUID`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:Entry.to_bytes -->
#### `Entry.to_bytes`

**Tipo:** funzione/metodo  
**Righe:** 169-171  
**Firma:** `def to_bytes(self) -> bytes`  
**Scopo:** Serializza/converte `to_bytes`.

**Chiamate dirette osservate nel corpo:** `asdict`, `encode`, `json.dumps`, `self.validate`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:Entry.from_bytes -->
#### `Entry.from_bytes`

**Tipo:** funzione/metodo  
**Righe:** 174-182  
**Firma:** `def from_bytes(cls, raw: bytes) -> 'Entry'`  
**Scopo:** Deserializza/costruisce `from_bytes`.

**Chiamate dirette osservate nel corpo:** `Action`, `TotpConfig`, `cls`, `data.get`, `data.setdefault`, `entry.validate`, `json.loads`, `raw.decode`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:CatalogItem -->
#### `CatalogItem`

**Tipo:** classe  
**Righe:** 186-196  
**Campi dichiarati:** `id`, `title`, `kind`, `usernames`, `tags`, `url_hosts`, `capabilities`, `revision`, `ciphertext_sha256`, `folder_id`  
**Responsabilità:** Una riga del catalogo derivata da una Entry e dall'hash del ciphertext.

<!-- symbol:keys_ng.models:Catalog -->
#### `Catalog`

**Tipo:** classe  
**Righe:** 200-218  
**Campi dichiarati:** `items`, `folders`, `schema`  
**Metodi:** `to_bytes`, `from_bytes`  
**Responsabilità:** Snapshot cifrato dei metadati ricercabili; ricostruibile dai record.

<!-- symbol:keys_ng.models:Catalog.to_bytes -->
#### `Catalog.to_bytes`

**Tipo:** funzione/metodo  
**Righe:** 205-206  
**Firma:** `def to_bytes(self) -> bytes`  
**Scopo:** Serializza/converte `to_bytes`.

**Chiamate dirette osservate nel corpo:** `asdict`, `encode`, `json.dumps`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.models:Catalog.from_bytes -->
#### `Catalog.from_bytes`

**Tipo:** funzione/metodo  
**Righe:** 209-218  
**Firma:** `def from_bytes(cls, raw: bytes) -> 'Catalog'`  
**Scopo:** Deserializza/costruisce `from_bytes`.

**Chiamate dirette osservate nel corpo:** `CatalogItem`, `Folder`, `ValueError`, `cls`, `data.get`, `item.setdefault`, `items.append`, `json.loads`, `raw.decode`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.platform.app_identity`

Identità desktop/processo e integrazione dell'icona applicativa.

**Sorgente:** `src/keys_ng/platform/app_identity.py`  
**Simboli eseguibili:** 4

**Dipendenze dirette del modulo:** `__future__`, `importlib.resources`, `sys`

<!-- symbol:keys_ng.platform.app_identity:icon_bytes -->
#### `icon_bytes`

**Tipo:** funzione/metodo  
**Righe:** 11-13  
**Firma:** `def icon_bytes() -> bytes`  
**Scopo:** Return the bundled legacy Keys application icon as PNG bytes.

**Chiamate dirette osservate nel corpo:** `files`, `joinpath`, `read_bytes`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.app_identity:configure_process_identity -->
#### `configure_process_identity`

**Tipo:** funzione/metodo  
**Righe:** 16-30  
**Firma:** `def configure_process_identity() -> None`  
**Scopo:** Set platform process identity before the GUI toolkit starts. On Windows this helps the taskbar group Keys NG separately from the Python interpreter when running from source. It is intentionally best-effort.

**Chiamate dirette osservate nel corpo:** `ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.app_identity:apply_qt_identity -->
#### `apply_qt_identity`

**Tipo:** funzione/metodo  
**Righe:** 33-57  
**Firma:** `def apply_qt_identity(app) -> object | None`  
**Scopo:** Apply application name, desktop identity and bundled icon to Qt. Returns the QIcon so callers can also set it explicitly on top-level windows if desired. Importing PySide6 is deferred to keep CLI/TUI free of a GUI dependency.

**Chiamate dirette osservate nel corpo:** `QIcon`, `QPixmap`, `app.setApplicationDisplayName`, `app.setApplicationName`, `app.setDesktopFileName`, `app.setOrganizationName`, `app.setWindowIcon`, `hasattr`, `icon_bytes`, `pixmap.loadFromData`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.app_identity:set_textual_terminal_title -->
#### `set_textual_terminal_title`

**Tipo:** funzione/metodo  
**Righe:** 60-75  
**Firma:** `def set_textual_terminal_title(app) -> None`  
**Scopo:** Best-effort TUI identity. A terminal application does not own the desktop window; the terminal emulator does. We can therefore set the terminal/window title where the host supports it, but cannot portably replace the terminal emulator's graphical taskbar icon from Textual.

**Chiamate dirette osservate nel corpo:** `app.console.set_window_title`.

**Attributi oggetto modificati:** `app.title`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.platform.desktop_integration`

Installazione/stato/rimozione del launcher desktop per utente.

**Sorgente:** `src/keys_ng/platform/desktop_integration.py`  
**Simboli eseguibili:** 13

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `importlib.resources`, `keys_ng.platform.app_identity`, `keys_ng.platform.host`, `os`, `pathlib`, `shutil`, `subprocess`, `sys`

<!-- symbol:keys_ng.platform.desktop_integration:DesktopIntegrationPaths -->
#### `DesktopIntegrationPaths`

**Tipo:** classe  
**Righe:** 21-25  
**Campi dichiarati:** `desktop_file`, `icon_file`  
**Responsabilità:** Implementa l'operazione `DesktopIntegrationPaths` in questo modulo.

<!-- symbol:keys_ng.platform.desktop_integration:_xdg_data_home -->
#### `_xdg_data_home`

**Tipo:** funzione/metodo  
**Righe:** 28-32  
**Firma:** `def _xdg_data_home() -> Path`  
**Scopo:** Helper interno che implementa `_xdg_data_home`.

**Chiamate dirette osservate nel corpo:** `Path`, `Path.home`, `expanduser`, `os.environ.get`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:_gui_executable -->
#### `_gui_executable`

**Tipo:** funzione/metodo  
**Righe:** 35-41  
**Firma:** `def _gui_executable() -> str`  
**Scopo:** Helper interno che implementa `_gui_executable`.

**Chiamate dirette osservate nel corpo:** `Path`, `resolve`, `shutil.which`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:user_paths -->
#### `user_paths`

**Tipo:** funzione/metodo  
**Righe:** 44-59  
**Firma:** `def user_paths() -> DesktopIntegrationPaths`  
**Scopo:** Implementa l'operazione `user_paths` in questo modulo.

**Chiamate dirette osservate nel corpo:** `DesktopIntegrationPaths`, `Path`, `Path.home`, `RuntimeError`, `_xdg_data_home`, `os.environ.get`, `sys.platform.startswith`.

**Eccezioni sollevate esplicitamente:** `RuntimeError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:_resource_bytes -->
#### `_resource_bytes`

**Tipo:** funzione/metodo  
**Righe:** 62-63  
**Firma:** `def _resource_bytes(name: str) -> bytes`  
**Scopo:** Helper interno che implementa `_resource_bytes`.

**Chiamate dirette osservate nel corpo:** `files`, `joinpath`, `read_bytes`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:_desktop_exec_token -->
#### `_desktop_exec_token`

**Tipo:** funzione/metodo  
**Righe:** 66-69  
**Firma:** `def _desktop_exec_token(value: str) -> str`  
**Scopo:** Helper interno che implementa `_desktop_exec_token`.

**Chiamate dirette osservate nel corpo:** `replace`, `value.replace`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:_install_linux -->
#### `_install_linux`

**Tipo:** funzione/metodo  
**Righe:** 72-95  
**Firma:** `def _install_linux(paths: DesktopIntegrationPaths) -> None`  
**Scopo:** Helper interno che implementa `_install_linux`.

**Chiamate dirette osservate nel corpo:** `Path`, `_desktop_exec_token`, `_gui_executable`, `_resource_bytes`, `decode`, `join`, `line.startswith`, `lines.append`, `name.lower`, `paths.desktop_file.chmod`, `paths.desktop_file.parent.mkdir`, `paths.desktop_file.write_text`, `paths.icon_file.chmod`, `paths.icon_file.parent.mkdir`, `paths.icon_file.write_bytes`, `startswith`, `template.splitlines`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:_install_windows -->
#### `_install_windows`

**Tipo:** funzione/metodo  
**Righe:** 98-125  
**Firma:** `def _install_windows(paths: DesktopIntegrationPaths) -> None`  
**Scopo:** Helper interno che implementa `_install_windows`.

**Chiamate dirette osservate nel corpo:** `Path`, `Path.home`, `RuntimeError`, `_gui_executable`, `_resource_bytes`, `arguments.replace`, `name.lower`, `paths.desktop_file.exists`, `paths.desktop_file.parent.mkdir`, `paths.icon_file.parent.mkdir`, `paths.icon_file.write_bytes`, `replace`, `shutil.which`, `startswith`, `str`, `subprocess.run`, `target.replace`.

**Eccezioni sollevate esplicitamente:** `RuntimeError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem, parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:_install_macos -->
#### `_install_macos`

**Tipo:** funzione/metodo  
**Righe:** 128-155  
**Firma:** `def _install_macos(paths: DesktopIntegrationPaths) -> None`  
**Scopo:** Helper interno che implementa `_install_macos`.

**Chiamate dirette osservate nel corpo:** `Path`, `_gui_executable`, `_resource_bytes`, `launcher.chmod`, `launcher.write_text`, `macos.mkdir`, `name.lower`, `paths.icon_file.write_bytes`, `resources.mkdir`, `startswith`, `write_text`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:install_user_desktop_integration -->
#### `install_user_desktop_integration`

**Tipo:** funzione/metodo  
**Righe:** 158-169  
**Firma:** `def install_user_desktop_integration() -> DesktopIntegrationPaths`  
**Scopo:** Install a per-user application-menu launcher on Linux, Windows or macOS.

**Chiamate dirette osservate nel corpo:** `RuntimeError`, `_install_linux`, `_install_macos`, `_install_windows`, `sys.platform.startswith`, `user_paths`.

**Eccezioni sollevate esplicitamente:** `RuntimeError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:ensure_user_desktop_integration -->
#### `ensure_user_desktop_integration`

**Tipo:** funzione/metodo  
**Righe:** 172-188  
**Firma:** `def ensure_user_desktop_integration() -> DesktopIntegrationPaths | None`  
**Scopo:** Best-effort per-user application-menu integration used by the GUI.

**Chiamate dirette osservate nel corpo:** `desktop_integration_status`, `in_flatpak`, `install_user_desktop_integration`, `sys.platform.startswith`, `user_paths`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 5 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:uninstall_user_desktop_integration -->
#### `uninstall_user_desktop_integration`

**Tipo:** funzione/metodo  
**Righe:** 191-201  
**Firma:** `def uninstall_user_desktop_integration() -> DesktopIntegrationPaths`  
**Scopo:** Implementa l'operazione `uninstall_user_desktop_integration` in questo modulo.

**Chiamate dirette osservate nel corpo:** `path.unlink`, `shutil.rmtree`, `user_paths`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.desktop_integration:desktop_integration_status -->
#### `desktop_integration_status`

**Tipo:** funzione/metodo  
**Righe:** 204-210  
**Firma:** `def desktop_integration_status() -> tuple[bool, DesktopIntegrationPaths]`  
**Scopo:** Implementa l'operazione `desktop_integration_status` in questo modulo.

**Chiamate dirette osservate nel corpo:** `is_file`, `paths.desktop_file.is_file`, `paths.icon_file.is_file`, `user_paths`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.platform.host`

Bridge Flatpak verso comandi host e risoluzione degli eseguibili.

**Sorgente:** `src/keys_ng/platform/host.py`  
**Simboli eseguibili:** 4

**Dipendenze dirette del modulo:** `__future__`, `os`, `pathlib`, `shutil`, `subprocess`

<!-- symbol:keys_ng.platform.host:in_flatpak -->
#### `in_flatpak`

**Tipo:** funzione/metodo  
**Righe:** 9-10  
**Firma:** `def in_flatpak() -> bool`  
**Scopo:** Implementa l'operazione `in_flatpak` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path`, `bool`, `exists`, `os.environ.get`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.host:host_prefix -->
#### `host_prefix`

**Tipo:** funzione/metodo  
**Righe:** 13-18  
**Firma:** `def host_prefix() -> list[str]`  
**Scopo:** Prefix argv so external desktop tools execute on the host from Flatpak.

**Chiamate dirette osservate nel corpo:** `in_flatpak`, `shutil.which`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.host:host_which -->
#### `host_which`

**Tipo:** funzione/metodo  
**Righe:** 21-37  
**Firma:** `def host_which(name: str) -> str | None`  
**Scopo:** Resolve an executable on the host without invoking a shell.

**Chiamate dirette osservate nel corpo:** `host_prefix`, `in_flatpak`, `os.access`, `os.path.isabs`, `os.path.isfile`, `proc.stdout.decode`, `shutil.which`, `splitlines`, `strip`, `subprocess.run`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 6 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.host:host_argv -->
#### `host_argv`

**Tipo:** funzione/metodo  
**Righe:** 40-41  
**Firma:** `def host_argv(argv: list[str]) -> list[str]`  
**Scopo:** Implementa l'operazione `host_argv` in questo modulo.

**Chiamate dirette osservate nel corpo:** `host_prefix`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.platform.paths`

Percorsi multipiattaforma per configurazione e dati applicativi.

**Sorgente:** `src/keys_ng/platform/paths.py`  
**Simboli eseguibili:** 2

**Dipendenze dirette del modulo:** `pathlib`, `platformdirs`

<!-- symbol:keys_ng.platform.paths:config_dir -->
#### `config_dir`

**Tipo:** funzione/metodo  
**Righe:** 9-10  
**Firma:** `def config_dir() -> Path`  
**Scopo:** Implementa l'operazione `config_dir` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path`, `user_config_path`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.platform.paths:data_dir -->
#### `data_dir`

**Tipo:** funzione/metodo  
**Righe:** 13-14  
**Firma:** `def data_dir() -> Path`  
**Scopo:** Implementa l'operazione `data_dir` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path`, `user_data_path`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.actions`

Avvia azioni URL, SSH, RDP e comandi basati su argv senza shell.

**Sorgente:** `src/keys_ng/services/actions.py`  
**Simboli eseguibili:** 9

**Dipendenze dirette del modulo:** `__future__`, `keys_ng.models`, `keys_ng.platform.host`, `keys_ng.storage.settings`, `os`, `shutil`, `subprocess`, `sys`, `urllib.parse`, `webbrowser`

<!-- symbol:keys_ng.services.actions:ActionError -->
#### `ActionError`

**Tipo:** classe  
**Righe:** 15-16  
**Basi:** `RuntimeError`  
**Responsabilità:** Implementa l'operazione `ActionError` in questo modulo.

<!-- symbol:keys_ng.services.actions:_which -->
#### `_which`

**Tipo:** funzione/metodo  
**Righe:** 19-23  
**Firma:** `def _which(name: str) -> str | None`  
**Scopo:** Helper interno che implementa `_which`.

**Chiamate dirette osservate nel corpo:** `host_which`, `in_flatpak`, `shutil.which`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.actions:_resolve_executable -->
#### `_resolve_executable`

**Tipo:** funzione/metodo  
**Righe:** 26-32  
**Firma:** `def _resolve_executable(name: str) -> str | None`  
**Scopo:** Resolve a configured executable without invoking a shell.

**Chiamate dirette osservate nel corpo:** `_which`, `in_flatpak`, `os.access`, `os.path.isabs`, `os.path.isfile`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.actions:_ssh_terminal -->
#### `_ssh_terminal`

**Tipo:** funzione/metodo  
**Righe:** 35-72  
**Firma:** `def _ssh_terminal(settings: AppSettings) -> tuple[str, list[str]]`  
**Scopo:** Helper interno che implementa `_ssh_terminal`.

**Chiamate dirette osservate nel corpo:** `ActionError`, `_resolve_executable`, `_which`, `get`, `list`, `os.path.basename`, `requested.lower`, `settings.ssh_terminal.strip`.

**Eccezioni sollevate esplicitamente:** `ActionError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.actions:_launch_ssh -->
#### `_launch_ssh`

**Tipo:** funzione/metodo  
**Righe:** 75-98  
**Firma:** `def _launch_ssh(action: Action, settings: AppSettings) -> None`  
**Scopo:** Helper interno che implementa `_launch_ssh`.

**Chiamate dirette osservate nel corpo:** `ActionError`, `_ssh_terminal`, `_which`, `host_argv`, `ssh_argv.append`, `ssh_argv.extend`, `str`, `subprocess.Popen`.

**Eccezioni sollevate esplicitamente:** `ActionError`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.actions:_linux_rdp -->
#### `_linux_rdp`

**Tipo:** funzione/metodo  
**Righe:** 101-117  
**Firma:** `def _linux_rdp(action: Action, settings: AppSettings) -> None`  
**Scopo:** Helper interno che implementa `_linux_rdp`.

**Chiamate dirette osservate nel corpo:** `ActionError`, `_resolve_executable`, `_which`, `argv.append`, `host_argv`, `next`, `requested.lower`, `settings.rdp_linux_client.strip`, `str`, `subprocess.Popen`.

**Eccezioni sollevate esplicitamente:** `ActionError`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.actions:_windows_rdp -->
#### `_windows_rdp`

**Tipo:** funzione/metodo  
**Righe:** 120-128  
**Firma:** `def _windows_rdp(action: Action, settings: AppSettings) -> None`  
**Scopo:** Helper interno che implementa `_windows_rdp`.

**Chiamate dirette osservate nel corpo:** `ActionError`, `_resolve_executable`, `host_argv`, `settings.rdp_windows_client.strip`, `str`, `subprocess.Popen`.

**Eccezioni sollevate esplicitamente:** `ActionError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.actions:_macos_rdp -->
#### `_macos_rdp`

**Tipo:** funzione/metodo  
**Righe:** 131-147  
**Firma:** `def _macos_rdp(action: Action, settings: AppSettings) -> None`  
**Scopo:** Helper interno che implementa `_macos_rdp`.

**Chiamate dirette osservate nel corpo:** `ActionError`, `_resolve_executable`, `attributes.append`, `host_argv`, `join`, `quote`, `requested.lower`, `settings.rdp_macos_client.strip`, `str`, `subprocess.Popen`.

**Eccezioni sollevate esplicitamente:** `ActionError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.actions:launch_action -->
#### `launch_action`

**Tipo:** funzione/metodo  
**Righe:** 150-173  
**Firma:** `def launch_action(action: Action, settings: AppSettings | None=None) -> None`  
**Scopo:** Valida e avvia `launch_action`.

**Chiamate dirette osservate nel corpo:** `ActionError`, `AppSettings.load`, `_launch_ssh`, `_linux_rdp`, `_macos_rdp`, `_windows_rdp`, `action.validate`, `host_argv`, `subprocess.Popen`, `webbrowser.open`.

**Eccezioni sollevate esplicitamente:** `ActionError`.

**Forma del flusso di controllo:** 8 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 4 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem, desktop URL launcher.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.clipboard`

Backend clipboard per segreti, verifica della proprietà e cancellazione temporizzata.

**Sorgente:** `src/keys_ng/services/clipboard.py`  
**Simboli eseguibili:** 9

**Dipendenze dirette del modulo:** `__future__`, `queue`, `secrets`, `shutil`, `subprocess`, `sys`, `threading`

<!-- symbol:keys_ng.services.clipboard:ClipboardUnavailable -->
#### `ClipboardUnavailable`

**Tipo:** classe  
**Righe:** 11-12  
**Basi:** `RuntimeError`  
**Responsabilità:** Implementa l'operazione `ClipboardUnavailable` in questo modulo.

<!-- symbol:keys_ng.services.clipboard:copy_secret_qt -->
#### `copy_secret_qt`

**Tipo:** funzione/metodo  
**Righe:** 15-40  
**Firma:** `def copy_secret_qt(secret: str, timeout_ms: int=15000) -> None`  
**Scopo:** Copy a secret using Qt and clear it only if Keys NG still owns the token.

**Chiamate dirette osservate nel corpo:** `ClipboardUnavailable`, `QByteArray`, `QGuiApplication.instance`, `QMimeData`, `QTimer.singleShot`, `app.clipboard`, `bytes`, `clipboard.clear`, `clipboard.mimeData`, `clipboard.setMimeData`, `current.data`, `mime.setData`, `mime.setText`, `secrets.token_bytes`.

**Eccezioni sollevate esplicitamente:** `ClipboardUnavailable`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard:copy_secret_qt.clear_if_owned -->
#### `copy_secret_qt.clear_if_owned`

**Tipo:** funzione/metodo  
**Righe:** 35-38  
**Firma:** `def clear_if_owned() -> None`  
**Scopo:** Implementa l'operazione `clear_if_owned` in questo modulo.

**Chiamate dirette osservate nel corpo:** `bytes`, `clipboard.clear`, `clipboard.mimeData`, `current.data`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard:_run_clipboard_command -->
#### `_run_clipboard_command`

**Tipo:** funzione/metodo  
**Righe:** 43-61  
**Firma:** `def _run_clipboard_command(argv: list[str], *, input_bytes: bytes | None=None, timeout: float=3.0) -> bytes`  
**Scopo:** Helper interno che implementa `_run_clipboard_command`.

**Chiamate dirette osservate nel corpo:** `ClipboardUnavailable`, `completed.stderr.decode`, `strip`, `subprocess.run`.

**Eccezioni sollevate esplicitamente:** `ClipboardUnavailable`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard:available_native_clipboard_backend -->
#### `available_native_clipboard_backend`

**Tipo:** funzione/metodo  
**Righe:** 64-88  
**Firma:** `def available_native_clipboard_backend() -> str | None`  
**Scopo:** Return the best terminal-friendly clipboard backend for this platform.

**Chiamate dirette osservate nel corpo:** `os.environ.get`, `shutil.which`.

**Forma del flusso di controllo:** 8 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 9 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard:set_native_clipboard -->
#### `set_native_clipboard`

**Tipo:** funzione/metodo  
**Righe:** 91-112  
**Firma:** `def set_native_clipboard(secret: str, backend: str | None=None) -> str`  
**Scopo:** Write text to a platform clipboard without putting the secret in argv/env.

**Chiamate dirette osservate nel corpo:** `ClipboardUnavailable`, `_run_clipboard_command`, `available_native_clipboard_backend`, `secret.encode`.

**Eccezioni sollevate esplicitamente:** `ClipboardUnavailable`.

**Forma del flusso di controllo:** 6 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, clipboard, parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard:read_native_clipboard -->
#### `read_native_clipboard`

**Tipo:** funzione/metodo  
**Righe:** 115-130  
**Firma:** `def read_native_clipboard(backend: str) -> str`  
**Scopo:** Implementa l'operazione `read_native_clipboard` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ClipboardUnavailable`, `_run_clipboard_command`, `data.decode`.

**Eccezioni sollevate esplicitamente:** `ClipboardUnavailable`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard:clear_native_clipboard -->
#### `clear_native_clipboard`

**Tipo:** funzione/metodo  
**Righe:** 133-155  
**Firma:** `def clear_native_clipboard(backend: str) -> None`  
**Scopo:** Implementa l'operazione `clear_native_clipboard` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ClipboardUnavailable`, `_run_clipboard_command`.

**Eccezioni sollevate esplicitamente:** `ClipboardUnavailable`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard:copy_secret_cli -->
#### `copy_secret_cli`

**Tipo:** funzione/metodo  
**Righe:** 158-214  
**Firma:** `def copy_secret_cli(secret: str, timeout_seconds: int=15) -> None`  
**Scopo:** Start a detached helper that owns/copies and later clears the clipboard. The helper prefers native terminal clipboard implementations. Qt is used only as a fallback, so the TUI no longer requires the GUI optional dependency.

**Chiamate dirette osservate nel corpo:** `ClipboardUnavailable`, `acknowledgement.startswith`, `acknowledgements.get`, `acknowledgements.put`, `decode`, `getattr`, `isinstance`, `proc.stderr.read`, `proc.stdin.close`, `proc.stdin.write`, `proc.stdout.close`, `proc.stdout.readline`, `proc.terminate`, `queue.Queue`, `raw_ack.decode`, `secret.encode`, `start`, `str`, `strip`, `subprocess.Popen`, `threading.Thread`.

**Eccezioni sollevate esplicitamente:** `ClipboardUnavailable`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 4 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem, clipboard, parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.clipboard_helper`

Processo helper distaccato usato dalle operazioni clipboard da terminale.

**Sorgente:** `src/keys_ng/services/clipboard_helper.py`  
**Simboli eseguibili:** 4

**Dipendenze dirette del modulo:** `__future__`, `keys_ng.services.clipboard`, `sys`, `time`

<!-- symbol:keys_ng.services.clipboard_helper:_normalise -->
#### `_normalise`

**Tipo:** funzione/metodo  
**Righe:** 14-16  
**Firma:** `def _normalise(value: str) -> str`  
**Scopo:** Helper interno che implementa `_normalise`.

**Chiamate dirette osservate nel corpo:** `value.replace`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard_helper:_native_worker -->
#### `_native_worker`

**Tipo:** funzione/metodo  
**Righe:** 19-33  
**Firma:** `def _native_worker(secret: str, timeout_seconds: int) -> None`  
**Scopo:** Helper interno che implementa `_native_worker`.

**Chiamate dirette osservate nel corpo:** `ClipboardUnavailable`, `_normalise`, `clear_native_clipboard`, `read_native_clipboard`, `set_native_clipboard`, `sys.stdout.flush`, `sys.stdout.write`, `time.sleep`.

**Eccezioni sollevate esplicitamente:** `ClipboardUnavailable`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard_helper:_qt_worker -->
#### `_qt_worker`

**Tipo:** funzione/metodo  
**Righe:** 36-53  
**Firma:** `def _qt_worker(secret: str, timeout_seconds: int) -> None`  
**Scopo:** Helper interno che implementa `_qt_worker`.

**Chiamate dirette osservate nel corpo:** `ClipboardUnavailable`, `QGuiApplication`, `QTimer.singleShot`, `app.clipboard`, `app.exec`, `app.processEvents`, `copy_secret_qt`, `sys.stdout.flush`, `sys.stdout.write`, `text`.

**Eccezioni sollevate esplicitamente:** `ClipboardUnavailable`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.clipboard_helper:main -->
#### `main`

**Tipo:** funzione/metodo  
**Righe:** 56-68  
**Firma:** `def main() -> None`  
**Scopo:** Implementa l'operazione `main` in questo modulo.

**Chiamate dirette osservate nel corpo:** `SystemExit`, `_native_worker`, `_qt_worker`, `decode`, `int`, `max`, `print`, `sys.stdin.buffer.read`.

**Eccezioni sollevate esplicitamente:** `SystemExit`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.diagnostics`

Logging diagnostico rotante opt-in con riepiloghi di operazioni e tempi che preservano la privacy.

**Sorgente:** `src/keys_ng/services/diagnostics.py`  
**Simboli eseguibili:** 6

**Dipendenze dirette del modulo:** `__future__`, `logging`, `logging.handlers`, `os`, `pathlib`, `platformdirs`, `sys`, `time`

<!-- symbol:keys_ng.services.diagnostics:default_log_path -->
#### `default_log_path`

**Tipo:** funzione/metodo  
**Righe:** 17-19  
**Firma:** `def default_log_path() -> Path`  
**Scopo:** Return the per-user diagnostics log path without creating it.

**Chiamate dirette osservate nel corpo:** `Path`, `user_log_dir`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.diagnostics:diagnostics_log_path -->
#### `diagnostics_log_path`

**Tipo:** funzione/metodo  
**Righe:** 22-24  
**Firma:** `def diagnostics_log_path() -> Path | None`  
**Scopo:** Return the active diagnostics log path, if diagnostics are configured.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.diagnostics:configure_diagnostics -->
#### `configure_diagnostics`

**Tipo:** funzione/metodo  
**Righe:** 27-73  
**Firma:** `def configure_diagnostics(settings, component: str) -> Path | None`  
**Scopo:** Configure rotating file diagnostics from AppSettings. Diagnostics are opt-in. Callers must never include credentials, decrypted record fields, TOTP seeds/codes, clipboard contents, or plaintext exports.

**Chiamate dirette osservate nel corpo:** `Path`, `RotatingFileHandler`, `default_log_path`, `expanduser`, `getattr`, `handler.setFormatter`, `int`, `logger.addHandler`, `logger.handlers.clear`, `logger.info`, `logger.setLevel`, `logging.Formatter`, `logging.getLogger`, `max`, `min`, `os.chmod`, `path.parent.mkdir`, `path.resolve`, `str`, `strip`, `sys.version.split`, `upper`.

**Attributi oggetto modificati:** `logger.propagate`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 3 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.diagnostics:get_logger -->
#### `get_logger`

**Tipo:** funzione/metodo  
**Righe:** 76-78  
**Firma:** `def get_logger(name: str) -> logging.Logger`  
**Scopo:** Return a child logger in the Keys NG diagnostics namespace.

**Chiamate dirette osservate nel corpo:** `logging.getLogger`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.diagnostics:elapsed_ms -->
#### `elapsed_ms`

**Tipo:** funzione/metodo  
**Righe:** 81-83  
**Firma:** `def elapsed_ms(start: float) -> float`  
**Scopo:** Convert a perf_counter start value to elapsed milliseconds.

**Chiamate dirette osservate nel corpo:** `time.perf_counter`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.diagnostics:safe_operation_args -->
#### `safe_operation_args`

**Tipo:** funzione/metodo  
**Righe:** 86-103  
**Firma:** `def safe_operation_args(args) -> str`  
**Scopo:** Return a non-secret summary of a GnuPG argv sequence. Only operation flags are exposed. Values following options are deliberately omitted so fingerprints, file names, UIDs, paths, and other arguments do not leak into diagnostic logs.

**Chiamate dirette osservate nel corpo:** `join`, `operation_flags.items`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.doctor`

Diagnostica dell'ambiente e del runtime.

**Sorgente:** `src/keys_ng/services/doctor.py`  
**Simboli eseguibili:** 3

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `importlib.util`, `keys_ng`, `keys_ng.crypto.backend`, `keys_ng.platform.desktop_integration`, `keys_ng.services.clipboard`, `keys_ng.services.diagnostics`, `keys_ng.storage.settings`, `platform`, `shutil`, `sys`

<!-- symbol:keys_ng.services.doctor:DoctorCheck -->
#### `DoctorCheck`

**Tipo:** classe  
**Righe:** 18-22  
**Campi dichiarati:** `name`, `ok`, `detail`, `optional`  
**Responsabilità:** Implementa l'operazione `DoctorCheck` in questo modulo.

<!-- symbol:keys_ng.services.doctor:_module -->
#### `_module`

**Tipo:** funzione/metodo  
**Righe:** 25-26  
**Firma:** `def _module(name: str) -> bool`  
**Scopo:** Helper interno che implementa `_module`.

**Chiamate dirette osservate nel corpo:** `importlib.util.find_spec`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.doctor:collect_doctor_checks -->
#### `collect_doctor_checks`

**Tipo:** funzione/metodo  
**Righe:** 29-74  
**Firma:** `def collect_doctor_checks(crypto: CryptoBackend, settings: AppSettings | None=None) -> list[DoctorCheck]`  
**Scopo:** Implementa l'operazione `collect_doctor_checks` in questo modulo.

**Chiamate dirette osservate nel corpo:** `AppSettings.default_path`, `AppSettings.load`, `DoctorCheck`, `_module`, `available_native_clipboard_backend`, `bool`, `checks.append`, `checks.extend`, `crypto.diagnose`, `default_log_path`, `desktop_integration_status`, `next`, `platform.python_version`, `shutil.which`, `str`, `sys.platform.startswith`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.entry_editor`

Bozza e validazione dell'editor credenziali indipendenti dal frontend, condivise da GUI e TUI.

**Sorgente:** `src/keys_ng/services/entry_editor.py`  
**Simboli eseguibili:** 3

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `keys_ng.i18n`, `keys_ng.models`, `keys_ng.services.ssh_options`, `keys_ng.services.totp`

<!-- symbol:keys_ng.services.entry_editor:EntryDraft -->
#### `EntryDraft`

**Tipo:** classe  
**Righe:** 12-56  
**Campi dichiarati:** `title`, `folder_id`, `action_type`, `username`, `password`, `url`, `host`, `port`, `ssh_x11_forwarding`, `ssh_options`, `tags`, `totp_uri`, `totp_secret`, `notes`  
**Metodi:** `from_entry`  
**Responsabilità:** Frontend-neutral editable representation of one credential. GUI and TUI deliberately use the same conversion routine so validation and preservation rules cannot silently diverge between front ends.

<!-- symbol:keys_ng.services.entry_editor:EntryDraft.from_entry -->
#### `EntryDraft.from_entry`

**Tipo:** funzione/metodo  
**Righe:** 35-56  
**Firma:** `def from_entry(cls, entry: Entry) -> 'EntryDraft'`  
**Scopo:** Deserializza/costruisce `from_entry`.

**Chiamate dirette osservate nel corpo:** `build_otpauth_uri`, `cls`, `format_ssh_options`, `join`, `next`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.entry_editor:build_entry_from_draft -->
#### `build_entry_from_draft`

**Tipo:** funzione/metodo  
**Righe:** 59-158  
**Firma:** `def build_entry_from_draft(draft: EntryDraft, existing: Entry | None=None) -> Entry`  
**Scopo:** Validate a frontend draft and create/update the domain Entry. Imported/legacy command actions and custom fields are preserved during an edit because the desktop editor does not expose them directly.

**Chiamate dirette osservate nel corpo:** `Action`, `Entry.create`, `ValueError`, `_`, `actions.insert`, `draft.action_type.strip`, `draft.host.strip`, `draft.port.strip`, `draft.tags.split`, `draft.title.strip`, `draft.totp_secret.strip`, `draft.totp_uri.strip`, `draft.url.strip`, `draft.username.strip`, `entry.validate`, `existing.validate`, `int`, `lower`, `parse_otpauth_uri`, `parse_ssh_options`, `secret.replace`, `tag.strip`, `token.secret.replace`, `totp_from_secret`, `upper`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Attributi oggetto modificati:** `existing.actions`, `existing.folder_id`, `existing.kind`, `existing.notes`, `existing.password`, `existing.revision`, `existing.tags`, `existing.title`, `existing.totp`, `existing.usernames`.

**Forma del flusso di controllo:** 10 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.passwords`

Generazione crittograficamente sicura di password.

**Sorgente:** `src/keys_ng/services/passwords.py`  
**Simboli eseguibili:** 1

**Dipendenze dirette del modulo:** `__future__`, `secrets`, `string`

<!-- symbol:keys_ng.services.passwords:generate_password -->
#### `generate_password`

**Tipo:** funzione/metodo  
**Righe:** 9-47  
**Firma:** `def generate_password(length: int=24, *, uppercase: bool=True, lowercase: bool=True, digits: bool=True, symbols: bool=True, ambiguous: bool=False) -> str`  
**Scopo:** Implementa l'operazione `generate_password` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ValueError`, `chars.extend`, `groups.append`, `join`, `len`, `range`, `secrets.choice`, `secrets.randbelow`, `set`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 8 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.qr`

Decodifica QR e conversione in configurazione TOTP.

**Sorgente:** `src/keys_ng/services/qr.py`  
**Simboli eseguibili:** 4

**Dipendenze dirette del modulo:** `__future__`, `keys_ng.models`, `keys_ng.services.totp`, `pathlib`

<!-- symbol:keys_ng.services.qr:QRUnavailable -->
#### `QRUnavailable`

**Tipo:** classe  
**Righe:** 9-10  
**Basi:** `RuntimeError`  
**Responsabilità:** Implementa l'operazione `QRUnavailable` in questo modulo.

<!-- symbol:keys_ng.services.qr:_decode_image -->
#### `_decode_image`

**Tipo:** funzione/metodo  
**Righe:** 13-24  
**Firma:** `def _decode_image(image) -> TotpConfig`  
**Scopo:** Helper interno che implementa `_decode_image`.

**Chiamate dirette osservate nel corpo:** `QRUnavailable`, `ValueError`, `barcode.text.strip`, `parse_otpauth_uri`, `text.startswith`, `zxingcpp.read_barcode`.

**Eccezioni sollevate esplicitamente:** `QRUnavailable`, `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.qr:parse_totp_qr_file -->
#### `parse_totp_qr_file`

**Tipo:** funzione/metodo  
**Righe:** 27-33  
**Firma:** `def parse_totp_qr_file(path: str | Path) -> TotpConfig`  
**Scopo:** Analizza e valida `parse_totp_qr_file`.

**Chiamate dirette osservate nel corpo:** `Image.open`, `Path`, `QRUnavailable`, `_decode_image`, `image.convert`.

**Eccezioni sollevate esplicitamente:** `QRUnavailable`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 1 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.qr:parse_totp_qimage -->
#### `parse_totp_qimage`

**Tipo:** funzione/metodo  
**Righe:** 36-37  
**Firma:** `def parse_totp_qimage(image) -> TotpConfig`  
**Scopo:** Analizza e valida `parse_totp_qimage`.

**Chiamate dirette osservate nel corpo:** `_decode_image`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.references`

Parsing e costruzione dei riferimenti UUID in stile KeePassXC.

**Sorgente:** `src/keys_ng/services/references.py`  
**Simboli eseguibili:** 5

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `keys_ng.errors`, `re`, `uuid`

<!-- symbol:keys_ng.services.references:EntryReference -->
#### `EntryReference`

**Tipo:** classe  
**Righe:** 15-21  
**Campi dichiarati:** `field`, `entry_id`  
**Metodi:** `field_name`  
**Responsabilità:** Implementa l'operazione `EntryReference` in questo modulo.

<!-- symbol:keys_ng.services.references:EntryReference.field_name -->
#### `EntryReference.field_name`

**Tipo:** funzione/metodo  
**Righe:** 20-21  
**Firma:** `def field_name(self) -> str`  
**Scopo:** Implementa l'operazione `field_name` in questo modulo.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.references:normalize_entry_uuid -->
#### `normalize_entry_uuid`

**Tipo:** funzione/metodo  
**Righe:** 24-28  
**Firma:** `def normalize_entry_uuid(value: str) -> str`  
**Scopo:** Implementa l'operazione `normalize_entry_uuid` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ReferenceError`, `str`, `uuid.UUID`, `value.strip`.

**Eccezioni sollevate esplicitamente:** `ReferenceError`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.references:parse_entry_reference -->
#### `parse_entry_reference`

**Tipo:** funzione/metodo  
**Righe:** 31-38  
**Firma:** `def parse_entry_reference(value: str | None) -> EntryReference | None`  
**Scopo:** Analizza e valida `parse_entry_reference`.

**Chiamate dirette osservate nel corpo:** `EntryReference`, `_REFERENCE_RE.fullmatch`, `match.groups`, `normalize_entry_uuid`, `value.strip`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.references:make_entry_reference -->
#### `make_entry_reference`

**Tipo:** funzione/metodo  
**Righe:** 41-47  
**Firma:** `def make_entry_reference(field: str, entry_id: str, *, keepass_uuid: bool=False) -> str`  
**Scopo:** Implementa l'operazione `make_entry_reference` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ReferenceError`, `field.upper`, `hex.upper`, `normalize_entry_uuid`, `strip`, `uuid.UUID`.

**Eccezioni sollevate esplicitamente:** `ReferenceError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.ssh_options`

Analizza e valida opzioni argv avanzate di OpenSSH.

**Sorgente:** `src/keys_ng/services/ssh_options.py`  
**Simboli eseguibili:** 4

**Dipendenze dirette del modulo:** `__future__`, `shlex`

<!-- symbol:keys_ng.services.ssh_options:SSHOptionsError -->
#### `SSHOptionsError`

**Tipo:** classe  
**Righe:** 6-7  
**Basi:** `ValueError`  
**Responsabilità:** Implementa l'operazione `SSHOptionsError` in questo modulo.

<!-- symbol:keys_ng.services.ssh_options:parse_ssh_options -->
#### `parse_ssh_options`

**Tipo:** funzione/metodo  
**Righe:** 10-26  
**Firma:** `def parse_ssh_options(text: str) -> list[str]`  
**Scopo:** Parse user-entered SSH options into argv without involving a shell. The destination, username, port and X11 forwarding are managed separately by Keys NG. We therefore reject options that would silently override those fields. All other OpenSSH options (including -J, -L, -R, -D and -o ...) are passed through as argv tokens.

**Chiamate dirette osservate nel corpo:** `SSHOptionsError`, `shlex.split`, `text.strip`, `validate_ssh_options`.

**Eccezioni sollevate esplicitamente:** `SSHOptionsError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.ssh_options:validate_ssh_options -->
#### `validate_ssh_options`

**Tipo:** funzione/metodo  
**Righe:** 29-52  
**Firma:** `def validate_ssh_options(argv: list[str]) -> None`  
**Scopo:** Valida gli invarianti di `validate_ssh_options`.

**Chiamate dirette osservate nel corpo:** `SSHOptionsError`, `enumerate`, `isdigit`, `len`, `lower`, `option_value.split`, `strip`, `token.startswith`.

**Eccezioni sollevate esplicitamente:** `SSHOptionsError`.

**Forma del flusso di controllo:** 9 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.ssh_options:format_ssh_options -->
#### `format_ssh_options`

**Tipo:** funzione/metodo  
**Righe:** 55-57  
**Firma:** `def format_ssh_options(argv: list[str]) -> str`  
**Scopo:** Return a safely quoted, editable representation of stored argv tokens.

**Chiamate dirette osservate nel corpo:** `shlex.join`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.totp`

Generazione TOTP e parsing/costruzione di URI otpauth.

**Sorgente:** `src/keys_ng/services/totp.py`  
**Simboli eseguibili:** 5

**Dipendenze dirette del modulo:** `__future__`, `base64`, `hashlib`, `hmac`, `keys_ng.models`, `struct`, `time`, `urllib.parse`

<!-- symbol:keys_ng.services.totp:_decode_base32 -->
#### `_decode_base32`

**Tipo:** funzione/metodo  
**Righe:** 15-18  
**Firma:** `def _decode_base32(secret: str) -> bytes`  
**Scopo:** Helper interno che implementa `_decode_base32`.

**Chiamate dirette osservate nel corpo:** `base64.b32decode`, `join`, `len`, `secret.split`, `upper`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.totp:totp_from_secret -->
#### `totp_from_secret`

**Tipo:** funzione/metodo  
**Righe:** 22-48  
**Firma:** `def totp_from_secret(secret: str, *, issuer: str='', account_name: str='', algorithm: str='SHA1', digits: int=6, period: int=30) -> TotpConfig`  
**Scopo:** Build and validate a TOTP configuration from a raw Base32 secret.

**Chiamate dirette osservate nel corpo:** `TotpConfig`, `ValueError`, `_decode_base32`, `account_name.strip`, `algorithm.upper`, `config.validate`, `issuer.strip`, `join`, `secret.split`, `upper`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.totp:generate_totp -->
#### `generate_totp`

**Tipo:** funzione/metodo  
**Righe:** 50-60  
**Firma:** `def generate_totp(config: TotpConfig, at_time: int | float | None=None) -> tuple[str, int]`  
**Scopo:** Implementa l'operazione `generate_totp` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_decode_base32`, `config.algorithm.upper`, `config.validate`, `digest`, `hmac.new`, `int`, `str`, `struct.pack`, `struct.unpack`, `time.time`, `zfill`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.totp:parse_otpauth_uri -->
#### `parse_otpauth_uri`

**Tipo:** funzione/metodo  
**Righe:** 63-84  
**Firma:** `def parse_otpauth_uri(uri: str) -> TotpConfig`  
**Scopo:** Analizza e valida `parse_otpauth_uri`.

**Chiamate dirette osservate nel corpo:** `TotpConfig`, `ValueError`, `config.validate`, `int`, `label.partition`, `params.get`, `parse_qs`, `parsed.netloc.lower`, `parsed.path.lstrip`, `unquote`, `upper`, `urlparse`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.totp:build_otpauth_uri -->
#### `build_otpauth_uri`

**Tipo:** funzione/metodo  
**Righe:** 87-98  
**Firma:** `def build_otpauth_uri(config: TotpConfig) -> str`  
**Scopo:** Costruisce `build_otpauth_uri`.

**Chiamate dirette osservate nel corpo:** `config.algorithm.upper`, `config.validate`, `join`, `params.append`, `quote`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.trusted_signers`

Lista di autorizzazione per-vault dei firmatari Inbox crittograficamente validi.

**Sorgente:** `src/keys_ng/services/trusted_signers.py`  
**Simboli eseguibili:** 7

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `keys_ng.crypto.backend`, `keys_ng.errors`, `keys_ng.storage.config`, `keys_ng.storage.vault`, `os`, `pathlib`

<!-- symbol:keys_ng.services.trusted_signers:TrustedSignerInfo -->
#### `TrustedSignerInfo`

**Tipo:** classe  
**Righe:** 14-21  
**Campi dichiarati:** `fingerprint`, `label`, `present`, `revoked`, `expired`, `can_sign`, `vault_signer`  
**Responsabilità:** Implementa l'operazione `TrustedSignerInfo` in questo modulo.

<!-- symbol:keys_ng.services.trusted_signers:_save_config -->
#### `_save_config`

**Tipo:** funzione/metodo  
**Righe:** 24-28  
**Firma:** `def _save_config(vault: Vault) -> None`  
**Scopo:** Helper interno che implementa `_save_config`.

**Chiamate dirette osservate nel corpo:** `os.chmod`, `path.write_text`, `vault.config.to_json`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.trusted_signers:_key_by_fingerprint -->
#### `_key_by_fingerprint`

**Tipo:** funzione/metodo  
**Righe:** 31-33  
**Firma:** `def _key_by_fingerprint(vault: Vault, fingerprint: str) -> KeyInfo | None`  
**Scopo:** Helper interno che implementa `_key_by_fingerprint`.

**Chiamate dirette osservate nel corpo:** `fingerprint.strip`, `key.fingerprint.upper`, `next`, `upper`, `vault.crypto.list_keys`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.trusted_signers:list_trusted_signers -->
#### `list_trusted_signers`

**Tipo:** funzione/metodo  
**Righe:** 36-54  
**Firma:** `def list_trusted_signers(vault: Vault) -> list[TrustedSignerInfo]`  
**Scopo:** Restituisce una vista filtrata/elencata di `list_trusted_signers`.

**Chiamate dirette osservate nel corpo:** `TrustedSignerInfo`, `bool`, `fingerprint.upper`, `key.fingerprint.upper`, `keys.get`, `result.append`, `upper`, `vault.crypto.list_keys`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.trusted_signers:eligible_signing_keys -->
#### `eligible_signing_keys`

**Tipo:** funzione/metodo  
**Righe:** 57-58  
**Firma:** `def eligible_signing_keys(vault: Vault) -> list[KeyInfo]`  
**Scopo:** Implementa l'operazione `eligible_signing_keys` in questo modulo.

**Chiamate dirette osservate nel corpo:** `vault.crypto.list_keys`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.trusted_signers:add_trusted_signer -->
#### `add_trusted_signer`

**Tipo:** funzione/metodo  
**Righe:** 61-76  
**Firma:** `def add_trusted_signer(vault: Vault, fingerprint: str) -> TrustedSignerInfo`  
**Scopo:** Implementa l'operazione `add_trusted_signer` in questo modulo.

**Chiamate dirette osservate nel corpo:** `TrustedSignerInfo`, `VaultError`, `_key_by_fingerprint`, `_save_config`, `upper`, `value.upper`, `vault.config.trusted_signers.append`, `vault.crypto.resolve_fingerprint`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.trusted_signers:remove_trusted_signer -->
#### `remove_trusted_signer`

**Tipo:** funzione/metodo  
**Righe:** 79-87  
**Firma:** `def remove_trusted_signer(vault: Vault, fingerprint: str) -> None`  
**Scopo:** Implementa l'operazione `remove_trusted_signer` in questo modulo.

**Chiamate dirette osservate nel corpo:** `VaultError`, `_save_config`, `fingerprint.strip`, `len`, `upper`, `value.upper`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Attributi oggetto modificati:** `vault.config.trusted_signers`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.ui_capabilities`

Dichiara il contratto di parità interattiva GUI/TUI.

**Sorgente:** `src/keys_ng/services/ui_capabilities.py`  
**Simboli eseguibili:** 1

**Dipendenze dirette del modulo:** `__future__`

<!-- symbol:keys_ng.services.ui_capabilities:missing_interactive_capabilities -->
#### `missing_interactive_capabilities`

**Tipo:** funzione/metodo  
**Righe:** 22-24  
**Firma:** `def missing_interactive_capabilities(frontend: str) -> frozenset[str]`  
**Scopo:** Implementa l'operazione `missing_interactive_capabilities` in questo modulo.

**Chiamate dirette osservate nel corpo:** `frozenset`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.vault_init`

Validazione condivisa della creazione vault, selezione chiavi e self-test crittografico prima della scrittura.

**Sorgente:** `src/keys_ng/services/vault_init.py`  
**Simboli eseguibili:** 7

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `keys_ng.crypto.backend`, `keys_ng.errors`, `keys_ng.storage.vault`, `pathlib`

<!-- symbol:keys_ng.services.vault_init:VaultInitRequest -->
#### `VaultInitRequest`

**Tipo:** classe  
**Righe:** 12-17  
**Campi dichiarati:** `path`, `recipients`, `signer`, `require_signature`, `catalog_privacy`  
**Responsabilità:** Implementa l'operazione `VaultInitRequest` in questo modulo.

<!-- symbol:keys_ng.services.vault_init:VaultInitChoices -->
#### `VaultInitChoices`

**Tipo:** classe  
**Righe:** 21-23  
**Campi dichiarati:** `recipients`, `signers`  
**Responsabilità:** Implementa l'operazione `VaultInitChoices` in questo modulo.

<!-- symbol:keys_ng.services.vault_init:available_vault_keys -->
#### `available_vault_keys`

**Tipo:** funzione/metodo  
**Righe:** 26-36  
**Firma:** `def available_vault_keys(crypto: CryptoBackend) -> VaultInitChoices`  
**Scopo:** Return usable public encryption keys and secret signing keys.

**Chiamate dirette osservate nel corpo:** `VaultInitChoices`, `crypto.list_keys`, `tuple`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_init:validate_vault_target -->
#### `validate_vault_target`

**Tipo:** funzione/metodo  
**Righe:** 39-54  
**Firma:** `def validate_vault_target(path: str | Path) -> Path`  
**Scopo:** Validate the target without creating or deleting user data.

**Chiamate dirette osservate nel corpo:** `Path`, `VaultError`, `any`, `expanduser`, `parent.exists`, `parent.is_dir`, `resolve`, `root.exists`, `root.is_dir`, `root.iterdir`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_init:_normalize_request -->
#### `_normalize_request`

**Tipo:** funzione/metodo  
**Righe:** 57-72  
**Firma:** `def _normalize_request(request: VaultInitRequest, crypto: CryptoBackend) -> VaultInitRequest`  
**Scopo:** Helper interno che implementa `_normalize_request`.

**Chiamate dirette osservate nel corpo:** `VaultError`, `VaultInitRequest`, `crypto.resolve_fingerprint`, `tuple`, `validate_vault_target`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_init:run_vault_crypto_self_test -->
#### `run_vault_crypto_self_test`

**Tipo:** funzione/metodo  
**Righe:** 75-86  
**Firma:** `def run_vault_crypto_self_test(crypto: CryptoBackend, recipients: tuple[str, ...], signer: str | None, require_signature: bool) -> None`  
**Scopo:** Verify encrypt/decrypt/signature behavior before writing a new vault.

**Chiamate dirette osservate nel corpo:** `VaultError`, `crypto.decrypt`, `crypto.encrypt`, `list`, `result.signer_fingerprint.upper`, `signer.upper`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_init:create_vault -->
#### `create_vault`

**Tipo:** funzione/metodo  
**Righe:** 89-106  
**Firma:** `def create_vault(request: VaultInitRequest, crypto: CryptoBackend, *, self_test: bool=True) -> Vault`  
**Scopo:** Create a vault through the shared CLI/GUI/TUI initialization policy.

**Chiamate dirette osservate nel corpo:** `Vault.init`, `_normalize_request`, `list`, `run_vault_crypto_self_test`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.services.vault_sessions`

Stato di sessione multi-vault per i frontend interattivi, mantenendo un oggetto Vault e lo stato lock/cache per ogni vault aperto.

**Sorgente:** `src/keys_ng/services/vault_sessions.py`  
**Simboli eseguibili:** 14

**Dipendenze dirette del modulo:** `__future__`, `collections.abc`, `keys_ng.storage.vault`, `pathlib`

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager -->
#### `VaultSessionManager`

**Tipo:** classe  
**Righe:** 9-82  
**Metodi:** `__init__`, `_key`, `active`, `active_path`, `add`, `activate`, `contains`, `opened`, `paths`, `close`, `lock_all`, `__len__`, `__iter__`  
**Responsabilità:** Track multiple open vault objects and one active vault. The manager deliberately keeps each ``Vault`` instance alive while it is open so its lock state and in-memory caches remain independent when the TUI switches between vaults.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.__init__ -->
#### `VaultSessionManager.__init__`

**Tipo:** funzione/metodo  
**Righe:** 17-20  
**Firma:** `def __init__(self, initial: Vault) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `self.add`.

**Attributi oggetto modificati:** `self._active_path`, `self._vaults`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager._key -->
#### `VaultSessionManager._key`

**Tipo:** funzione/metodo  
**Righe:** 23-24  
**Firma:** `def _key(path: str | Path) -> str`  
**Scopo:** Helper interno che implementa `_key`.

**Chiamate dirette osservate nel corpo:** `Path`, `expanduser`, `resolve`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.active -->
#### `VaultSessionManager.active`

**Tipo:** funzione/metodo  
**Righe:** 27-28  
**Firma:** `def active(self) -> Vault`  
**Scopo:** Implementa l'operazione `active` in questo modulo.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.active_path -->
#### `VaultSessionManager.active_path`

**Tipo:** funzione/metodo  
**Righe:** 31-32  
**Firma:** `def active_path(self) -> str`  
**Scopo:** Implementa l'operazione `active_path` in questo modulo.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.add -->
#### `VaultSessionManager.add`

**Tipo:** funzione/metodo  
**Righe:** 34-42  
**Firma:** `def add(self, vault: Vault, *, activate: bool=True) -> Vault`  
**Scopo:** Implementa l'operazione `add` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self._key`, `self._vaults.get`.

**Attributi oggetto modificati:** `self._active_path`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.activate -->
#### `VaultSessionManager.activate`

**Tipo:** funzione/metodo  
**Righe:** 44-49  
**Firma:** `def activate(self, path: str | Path) -> Vault`  
**Scopo:** Implementa l'operazione `activate` in questo modulo.

**Chiamate dirette osservate nel corpo:** `KeyError`, `self._key`.

**Eccezioni sollevate esplicitamente:** `KeyError`.

**Attributi oggetto modificati:** `self._active_path`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.contains -->
#### `VaultSessionManager.contains`

**Tipo:** funzione/metodo  
**Righe:** 51-52  
**Firma:** `def contains(self, path: str | Path) -> bool`  
**Scopo:** Implementa l'operazione `contains` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self._key`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.opened -->
#### `VaultSessionManager.opened`

**Tipo:** funzione/metodo  
**Righe:** 54-55  
**Firma:** `def opened(self) -> tuple[Vault, ...]`  
**Scopo:** Implementa l'operazione `opened` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self._vaults.values`, `tuple`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.paths -->
#### `VaultSessionManager.paths`

**Tipo:** funzione/metodo  
**Righe:** 57-58  
**Firma:** `def paths(self) -> tuple[str, ...]`  
**Scopo:** Implementa l'operazione `paths` in questo modulo.

**Chiamate dirette osservate nel corpo:** `tuple`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.close -->
#### `VaultSessionManager.close`

**Tipo:** funzione/metodo  
**Righe:** 60-72  
**Firma:** `def close(self, path: str | Path | None=None) -> Vault | None`  
**Scopo:** Implementa l'operazione `close` in questo modulo.

**Chiamate dirette osservate nel corpo:** `next`, `reversed`, `self._key`, `self._vaults.pop`, `vault.lock`.

**Attributi oggetto modificati:** `self._active_path`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.lock_all -->
#### `VaultSessionManager.lock_all`

**Tipo:** funzione/metodo  
**Righe:** 74-76  
**Firma:** `def lock_all(self) -> None`  
**Scopo:** Implementa l'operazione `lock_all` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self._vaults.values`, `vault.lock`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.__len__ -->
#### `VaultSessionManager.__len__`

**Tipo:** funzione/metodo  
**Righe:** 78-79  
**Firma:** `def __len__(self) -> int`  
**Scopo:** Helper interno che implementa `__len__`.

**Chiamate dirette osservate nel corpo:** `len`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.services.vault_sessions:VaultSessionManager.__iter__ -->
#### `VaultSessionManager.__iter__`

**Tipo:** funzione/metodo  
**Righe:** 81-82  
**Firma:** `def __iter__(self) -> Iterable[Vault]`  
**Scopo:** Helper interno che implementa `__iter__`.

**Chiamate dirette osservate nel corpo:** `iter`, `self._vaults.values`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.storage.atomic`

Sostituzione atomica crash-resistant di soli ciphertext e pulizia dei temporanei residui.

**Sorgente:** `src/keys_ng/storage/atomic.py`  
**Simboli eseguibili:** 2

**Dipendenze dirette del modulo:** `__future__`, `os`, `pathlib`, `secrets`

<!-- symbol:keys_ng.storage.atomic:atomic_write_ciphertext -->
#### `atomic_write_ciphertext`

**Tipo:** funzione/metodo  
**Righe:** 8-32  
**Firma:** `def atomic_write_ciphertext(path: Path, data: bytes) -> None`  
**Scopo:** Atomically replace a ciphertext file. The temporary file contains ciphertext only.

**Chiamate dirette osservate nel corpo:** `handle.fileno`, `handle.flush`, `handle.write`, `hasattr`, `os.close`, `os.fdopen`, `os.fsync`, `os.open`, `os.replace`, `path.parent.mkdir`, `path.with_name`, `secrets.token_hex`, `tmp.unlink`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 3 blocchi try, 1 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.atomic:remove_stale_ciphertext_temps -->
#### `remove_stale_ciphertext_temps`

**Tipo:** funzione/metodo  
**Righe:** 35-46  
**Firma:** `def remove_stale_ciphertext_temps(directory: Path) -> int`  
**Scopo:** Remove abandoned atomic-write temp files. They contain ciphertext only.

**Chiamate dirette osservate nel corpo:** `directory.exists`, `directory.glob`, `path.unlink`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.storage.config`

Modello del file di policy/configurazione in chiaro del vault.

**Sorgente:** `src/keys_ng/storage/config.py`  
**Simboli eseguibili:** 4

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `json`, `keys_ng.errors`, `pathlib`

<!-- symbol:keys_ng.storage.config:VaultConfig -->
#### `VaultConfig`

**Tipo:** classe  
**Righe:** 14-59  
**Campi dichiarati:** `recipients`, `signer`, `trusted_signers`, `require_signature`, `catalog_privacy`, `schema`  
**Metodi:** `validate`, `to_json`, `load`  
**Responsabilità:** Implementa l'operazione `VaultConfig` in questo modulo.

<!-- symbol:keys_ng.storage.config:VaultConfig.validate -->
#### `VaultConfig.validate`

**Tipo:** funzione/metodo  
**Righe:** 22-30  
**Firma:** `def validate(self) -> None`  
**Scopo:** Valida gli invarianti di `validate`.

**Chiamate dirette osservate nel corpo:** `VaultError`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.config:VaultConfig.to_json -->
#### `VaultConfig.to_json`

**Tipo:** funzione/metodo  
**Righe:** 32-45  
**Firma:** `def to_json(self) -> str`  
**Scopo:** Serializza/converte `to_json`.

**Chiamate dirette osservate nel corpo:** `json.dumps`, `self.validate`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.config:VaultConfig.load -->
#### `VaultConfig.load`

**Tipo:** funzione/metodo  
**Righe:** 48-59  
**Firma:** `def load(cls, vault_path: Path) -> 'VaultConfig'`  
**Scopo:** Implementa l'operazione `load` in questo modulo.

**Chiamate dirette osservate nel corpo:** `VaultError`, `cls`, `config.validate`, `data.get`, `data.setdefault`, `json.loads`, `path.read_text`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.storage.inbox`

Deposito con sola chiave pubblica e import controllato dell'inbox.

**Sorgente:** `src/keys_ng/storage/inbox.py`  
**Simboli eseguibili:** 11

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `keys_ng.crypto.backend`, `keys_ng.models`, `keys_ng.services.diagnostics`, `keys_ng.storage.atomic`, `keys_ng.storage.vault`, `pathlib`, `time`, `uuid`

<!-- symbol:keys_ng.storage.inbox:InboxInspection -->
#### `InboxInspection`

**Tipo:** classe  
**Righe:** 18-44  
**Campi dichiarati:** `path`, `entry`, `decryptable`, `signed`, `signature_valid`, `signer_fingerprint`, `signer_authorized`, `error`  
**Metodi:** `importable`, `status`  
**Responsabilità:** Implementa l'operazione `InboxInspection` in questo modulo.

<!-- symbol:keys_ng.storage.inbox:InboxInspection.importable -->
#### `InboxInspection.importable`

**Tipo:** funzione/metodo  
**Righe:** 29-30  
**Firma:** `def importable(self) -> bool`  
**Scopo:** Implementa l'operazione `importable` in questo modulo.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:InboxInspection.status -->
#### `InboxInspection.status`

**Tipo:** funzione/metodo  
**Righe:** 33-44  
**Firma:** `def status(self) -> str`  
**Scopo:** Implementa l'operazione `status` in questo modulo.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 6 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:write_encrypted_entry -->
#### `write_encrypted_entry`

**Tipo:** funzione/metodo  
**Righe:** 47-53  
**Firma:** `def write_encrypted_entry(output_path: str | Path, entry: Entry, crypto: CryptoBackend, recipients: list[str], signer: str | None=None) -> Path`  
**Scopo:** Encrypt one standalone entry to an arbitrary ciphertext path.

**Chiamate dirette osservate nel corpo:** `Path`, `atomic_write_ciphertext`, `crypto.encrypt`, `entry.to_bytes`, `entry.validate`, `expanduser`, `resolve`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:deposit_entry -->
#### `deposit_entry`

**Tipo:** funzione/metodo  
**Righe:** 56-59  
**Firma:** `def deposit_entry(vault_path: str | Path, entry: Entry, crypto: CryptoBackend, recipients: list[str], signer: str | None=None) -> Path`  
**Scopo:** Write a new encrypted inbox item without requiring access to the vault catalog.

**Chiamate dirette osservate nel corpo:** `Path`, `expanduser`, `resolve`, `uuid.uuid4`, `write_encrypted_entry`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:pending_inbox_paths -->
#### `pending_inbox_paths`

**Tipo:** funzione/metodo  
**Righe:** 62-64  
**Firma:** `def pending_inbox_paths(vault: Vault) -> list[Path]`  
**Scopo:** Return pending ciphertexts without decrypting them.

**Chiamate dirette osservate nel corpo:** `glob`, `sorted`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:inspect_inbox_item -->
#### `inspect_inbox_item`

**Tipo:** funzione/metodo  
**Righe:** 67-89  
**Firma:** `def inspect_inbox_item(vault: Vault, path: Path) -> InboxInspection`  
**Scopo:** Decrypt and classify one inbox item without modifying the vault.

**Chiamate dirette osservate nel corpo:** `Entry.from_bytes`, `InboxInspection`, `_LOG.debug`, `_LOG.info`, `bool`, `elapsed_ms`, `fp.upper`, `path.read_bytes`, `signer.upper`, `time.perf_counter`, `type`, `vault.crypto.decrypt`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 3 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:inspect_inbox -->
#### `inspect_inbox`

**Tipo:** funzione/metodo  
**Righe:** 92-95  
**Firma:** `def inspect_inbox(vault: Vault) -> list[InboxInspection]`  
**Scopo:** Implementa l'operazione `inspect_inbox` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_LOG.info`, `inspect_inbox_item`, `len`, `pending_inbox_paths`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:import_inbox_item -->
#### `import_inbox_item`

**Tipo:** funzione/metodo  
**Righe:** 98-118  
**Firma:** `def import_inbox_item(vault: Vault, inspection: InboxInspection, *, delete_after: bool=True, accept_unsigned: bool=False) -> str`  
**Scopo:** Import one already inspected item and re-encrypt/sign it with vault policy.

**Chiamate dirette osservate nel corpo:** `ValueError`, `_LOG.debug`, `_LOG.info`, `elapsed_ms`, `inspection.path.unlink`, `target.exists`, `time.perf_counter`, `vault.save_entry`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 7 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:delete_inbox_item -->
#### `delete_inbox_item`

**Tipo:** funzione/metodo  
**Righe:** 121-126  
**Firma:** `def delete_inbox_item(vault: Vault, path: Path) -> None`  
**Scopo:** Elimina `delete_inbox_item`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `path.resolve`, `resolve`, `resolved.suffix.lower`, `resolved.unlink`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.inbox:import_inbox -->
#### `import_inbox`

**Tipo:** funzione/metodo  
**Righe:** 129-138  
**Firma:** `def import_inbox(vault: Vault, *, delete_after: bool=True, accept_unsigned: bool=False) -> list[tuple[Path, str]]`  
**Scopo:** Import all inbox records, preserving failed source files.

**Chiamate dirette osservate nel corpo:** `import_inbox_item`, `inspect_inbox`, `results.append`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.storage.settings`

Impostazioni applicative TOML per utente.

**Sorgente:** `src/keys_ng/storage/settings.py`  
**Simboli eseguibili:** 8

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `os`, `pathlib`, `platformdirs`, `tomllib`

<!-- symbol:keys_ng.storage.settings:_string_list -->
#### `_string_list`

**Tipo:** funzione/metodo  
**Righe:** 11-16  
**Firma:** `def _string_list(value, name: str) -> list[str]`  
**Scopo:** Helper interno che implementa `_string_list`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `all`, `isinstance`, `list`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.settings:_toml_string -->
#### `_toml_string`

**Tipo:** funzione/metodo  
**Righe:** 19-20  
**Firma:** `def _toml_string(value: str) -> str`  
**Scopo:** Helper interno che implementa `_toml_string`.

**Chiamate dirette osservate nel corpo:** `replace`, `value.replace`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.settings:_toml_array -->
#### `_toml_array`

**Tipo:** funzione/metodo  
**Righe:** 23-24  
**Firma:** `def _toml_array(values: list[str]) -> str`  
**Scopo:** Helper interno che implementa `_toml_array`.

**Chiamate dirette osservate nel corpo:** `_toml_string`, `join`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.settings:AppSettings -->
#### `AppSettings`

**Tipo:** classe  
**Righe:** 28-164  
**Campi dichiarati:** `language`, `clipboard_password_timeout`, `clipboard_totp_timeout`, `auto_lock_timeout`, `crypto_backend`, `gpg_executable`, `gpgconf_executable`, `tree_startup_view`, `recent_vaults`, `tui_clipboard_notice_background`, `tui_clipboard_notice_foreground`, `tui_clipboard_notice_seconds`, `diagnostics_enabled`, `diagnostics_level`, `diagnostics_log_file`, `diagnostics_max_bytes`, `diagnostics_backup_count`, `ssh_terminal`, `ssh_terminal_options`, `rdp_linux_client`, `rdp_linux_options`, `rdp_windows_client`, `rdp_windows_options`, `rdp_macos_client`, `rdp_macos_options`  
**Metodi:** `default_path`, `load`, `remember_vault`, `save`  
**Responsabilità:** Preferenze applicative validate caricate/salvate in TOML.

<!-- symbol:keys_ng.storage.settings:AppSettings.default_path -->
#### `AppSettings.default_path`

**Tipo:** funzione/metodo  
**Righe:** 60-61  
**Firma:** `def default_path(cls) -> Path`  
**Scopo:** Implementa l'operazione `default_path` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path`, `user_config_dir`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.settings:AppSettings.load -->
#### `AppSettings.load`

**Tipo:** funzione/metodo  
**Righe:** 64-113  
**Firma:** `def load(cls, path: Path | None=None) -> 'AppSettings'`  
**Scopo:** Implementa l'operazione `load` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ValueError`, `_string_list`, `bool`, `clipboard.get`, `cls`, `cls.default_path`, `data.get`, `diagnostics.get`, `float`, `gnupg.get`, `int`, `launchers.get`, `lower`, `max`, `min`, `path.exists`, `path.open`, `rdp.get`, `rdp_linux.get`, `rdp_macos.get`, `rdp_windows.get`, `security.get`, `ssh.get`, `str`, `strip`, `tomllib.load`, `tui.get`, `ui.get`, `upper`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 1 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, clipboard, parser/serialization.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.settings:AppSettings.remember_vault -->
#### `AppSettings.remember_vault`

**Tipo:** funzione/metodo  
**Righe:** 116-119  
**Firma:** `def remember_vault(self, path: str | Path) -> None`  
**Scopo:** Implementa l'operazione `remember_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path`, `expanduser`, `resolve`, `str`.

**Attributi oggetto modificati:** `self.recent_vaults`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.settings:AppSettings.save -->
#### `AppSettings.save`

**Tipo:** funzione/metodo  
**Righe:** 121-164  
**Firma:** `def save(self, path: Path | None=None) -> Path`  
**Scopo:** Valida e persiste lo stato per `save`.

**Chiamate dirette osservate nel corpo:** `_toml_array`, `_toml_string`, `lower`, `os.chmod`, `path.parent.mkdir`, `path.write_text`, `self.default_path`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.storage.vault`

Servizio centrale del vault: cifratura, firme, catalogo, record, cartelle, riferimenti e binding d'integrità.

**Sorgente:** `src/keys_ng/storage/vault.py`  
**Simboli eseguibili:** 42

**Dipendenze dirette del modulo:** `__future__`, `dataclasses`, `hashlib`, `keys_ng.crypto.backend`, `keys_ng.errors`, `keys_ng.models`, `keys_ng.services.diagnostics`, `keys_ng.services.references`, `keys_ng.storage.atomic`, `keys_ng.storage.config`, `os`, `pathlib`, `time`, `urllib.parse`

<!-- symbol:keys_ng.storage.vault:Vault -->
#### `Vault`

**Tipo:** classe  
**Righe:** 26-544  
**Metodi:** `__init__`, `init`, `recover_interrupted_writes`, `locked`, `lock`, `unlock`, `_require_unlocked`, `_verify`, `_encrypt`, `_decrypt`, `_write_catalog`, `_write_folders`, `load_catalog`, `load_folders`, `_catalog_item`, `_sync_catalog_folders`, `save_entry`, `_verify_record_binding`, `get_entry`, `resolve_reference_value`, `resolved_username`, `resolved_password`, `resolved_action`, `delete_entry`, `list_items`, `_folder_paths_from`, `folder_paths`, `search`, `reindex`, `catalog_health`, `list_folders`, `get_folder`, `folder_path`, `resolve_folder_path`, `create_folder`, `create_folder_path`, `rename_folder`, `move_folder`, `delete_folder`, `move_entry`  
**Responsabilità:** Rappresenta un singolo vault e ne applica la policy di storage/sicurezza.

<!-- symbol:keys_ng.storage.vault:Vault.__init__ -->
#### `Vault.__init__`

**Tipo:** funzione/metodo  
**Righe:** 27-37  
**Firma:** `def __init__(self, path: str | Path, crypto: CryptoBackend) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `Path`, `VaultConfig.load`, `expanduser`, `resolve`, `self.recover_interrupted_writes`.

**Attributi oggetto modificati:** `self._catalog_cache`, `self._folders_cache`, `self._locked`, `self.config`, `self.crypto`, `self.path`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.init -->
#### `Vault.init`

**Tipo:** funzione/metodo  
**Righe:** 40-67  
**Firma:** `def init(cls, path: str | Path, crypto: CryptoBackend, recipients: list[str], signer: str | None, require_signature: bool=True, catalog_privacy: str='standard') -> 'Vault'`  
**Scopo:** Implementa l'operazione `init` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Catalog`, `FolderStore`, `Path`, `VaultConfig`, `VaultError`, `any`, `cls`, `config.to_json`, `config_path.write_text`, `expanduser`, `mkdir`, `os.chmod`, `resolve`, `root.exists`, `root.iterdir`, `vault._write_catalog`, `vault._write_folders`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.recover_interrupted_writes -->
#### `Vault.recover_interrupted_writes`

**Tipo:** funzione/metodo  
**Righe:** 69-73  
**Firma:** `def recover_interrupted_writes(self) -> int`  
**Scopo:** Implementa l'operazione `recover_interrupted_writes` in questo modulo.

**Chiamate dirette osservate nel corpo:** `remove_stale_ciphertext_temps`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.locked -->
#### `Vault.locked`

**Tipo:** funzione/metodo  
**Righe:** 76-77  
**Firma:** `def locked(self) -> bool`  
**Scopo:** Implementa l'operazione `locked` in questo modulo.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.lock -->
#### `Vault.lock`

**Tipo:** funzione/metodo  
**Righe:** 79-84  
**Firma:** `def lock(self, hard: bool=False) -> None`  
**Scopo:** Implementa l'operazione `lock` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.crypto.hard_lock`.

**Attributi oggetto modificati:** `self._catalog_cache`, `self._folders_cache`, `self._locked`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.unlock -->
#### `Vault.unlock`

**Tipo:** funzione/metodo  
**Righe:** 86-93  
**Firma:** `def unlock(self) -> None`  
**Scopo:** Implementa l'operazione `unlock` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.load_catalog`, `self.load_folders`.

**Attributi oggetto modificati:** `self._locked`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._require_unlocked -->
#### `Vault._require_unlocked`

**Tipo:** funzione/metodo  
**Righe:** 95-97  
**Firma:** `def _require_unlocked(self) -> None`  
**Scopo:** Helper interno che implementa `_require_unlocked`.

**Chiamate dirette osservate nel corpo:** `VaultError`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._verify -->
#### `Vault._verify`

**Tipo:** funzione/metodo  
**Righe:** 99-107  
**Firma:** `def _verify(self, signer_fingerprint: str | None, signature_valid: bool, primary_signer_fingerprint: str | None=None) -> None`  
**Scopo:** Helper interno che implementa `_verify`.

**Chiamate dirette osservate nel corpo:** `SignatureError`, `fp.upper`, `upper`.

**Eccezioni sollevate esplicitamente:** `SignatureError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._encrypt -->
#### `Vault._encrypt`

**Tipo:** funzione/metodo  
**Righe:** 109-111  
**Firma:** `def _encrypt(self, plaintext: bytes) -> bytes`  
**Scopo:** Helper interno che implementa `_encrypt`.

**Chiamate dirette osservate nel corpo:** `self._require_unlocked`, `self.crypto.encrypt`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._decrypt -->
#### `Vault._decrypt`

**Tipo:** funzione/metodo  
**Righe:** 113-117  
**Firma:** `def _decrypt(self, ciphertext: bytes) -> bytes`  
**Scopo:** Helper interno che implementa `_decrypt`.

**Chiamate dirette osservate nel corpo:** `self._require_unlocked`, `self._verify`, `self.crypto.decrypt`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._write_catalog -->
#### `Vault._write_catalog`

**Tipo:** funzione/metodo  
**Righe:** 119-122  
**Firma:** `def _write_catalog(self, catalog: Catalog) -> None`  
**Scopo:** Helper interno che implementa `_write_catalog`.

**Chiamate dirette osservate nel corpo:** `atomic_write_ciphertext`, `catalog.to_bytes`, `self._encrypt`.

**Attributi oggetto modificati:** `self._catalog_cache`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._write_folders -->
#### `Vault._write_folders`

**Tipo:** funzione/metodo  
**Righe:** 124-127  
**Firma:** `def _write_folders(self, store: FolderStore) -> None`  
**Scopo:** Helper interno che implementa `_write_folders`.

**Chiamate dirette osservate nel corpo:** `atomic_write_ciphertext`, `self._encrypt`, `store.to_bytes`.

**Attributi oggetto modificati:** `self._folders_cache`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.load_catalog -->
#### `Vault.load_catalog`

**Tipo:** funzione/metodo  
**Righe:** 129-138  
**Firma:** `def load_catalog(self) -> Catalog`  
**Scopo:** Carica e valida `load_catalog`.

**Chiamate dirette osservate nel corpo:** `Catalog`, `Catalog.from_bytes`, `path.exists`, `path.read_bytes`, `self._decrypt`, `self._require_unlocked`.

**Attributi oggetto modificati:** `self._catalog_cache`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.load_folders -->
#### `Vault.load_folders`

**Tipo:** funzione/metodo  
**Righe:** 140-151  
**Firma:** `def load_folders(self) -> FolderStore`  
**Scopo:** Carica e valida `load_folders`.

**Chiamate dirette osservate nel corpo:** `FolderStore`, `FolderStore.from_bytes`, `list`, `path.exists`, `path.read_bytes`, `self._decrypt`, `self._require_unlocked`, `self.load_catalog`.

**Attributi oggetto modificati:** `self._folders_cache`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._catalog_item -->
#### `Vault._catalog_item`

**Tipo:** funzione/metodo  
**Righe:** 153-182  
**Firma:** `def _catalog_item(self, entry: Entry, ciphertext: bytes) -> CatalogItem`  
**Scopo:** Helper interno che implementa `_catalog_item`.

**Chiamate dirette osservate nel corpo:** `CatalogItem`, `capabilities.append`, `capabilities.extend`, `hexdigest`, `hosts.append`, `set`, `sha256`, `sorted`, `urlparse`.

**Forma del flusso di controllo:** 6 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._sync_catalog_folders -->
#### `Vault._sync_catalog_folders`

**Tipo:** funzione/metodo  
**Righe:** 184-188  
**Firma:** `def _sync_catalog_folders(self, catalog: Catalog | None=None, store: FolderStore | None=None) -> Catalog`  
**Scopo:** Helper interno che implementa `_sync_catalog_folders`.

**Chiamate dirette osservate nel corpo:** `list`, `self.load_catalog`, `self.load_folders`.

**Attributi oggetto modificati:** `catalog.folders`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.save_entry -->
#### `Vault.save_entry`

**Tipo:** funzione/metodo  
**Righe:** 190-205  
**Firma:** `def save_entry(self, entry: Entry) -> Entry`  
**Scopo:** Valida e persiste lo stato per `save_entry`.

**Chiamate dirette osservate nel corpo:** `VaultError`, `atomic_write_ciphertext`, `catalog.items.append`, `catalog.items.sort`, `entry.to_bytes`, `entry.validate`, `self._catalog_item`, `self._encrypt`, `self._require_unlocked`, `self._sync_catalog_folders`, `self._write_catalog`, `self.load_catalog`, `self.load_folders`, `utc_now`, `x.title.casefold`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Attributi oggetto modificati:** `catalog.items`, `entry.updated_at`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._verify_record_binding -->
#### `Vault._verify_record_binding`

**Tipo:** funzione/metodo  
**Righe:** 207-223  
**Firma:** `def _verify_record_binding(self, entry_id: str, ciphertext: bytes, entry: Entry) -> None`  
**Scopo:** Bind a decrypted record to its signed catalog snapshot. This detects replacement or rollback of a single record while the catalog remains current. It intentionally does not claim protection against an attacker who rolls back the record and the signed catalog together.

**Chiamate dirette osservate nel corpo:** `VaultError`, `hexdigest`, `next`, `self.load_catalog`, `sha256`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.get_entry -->
#### `Vault.get_entry`

**Tipo:** funzione/metodo  
**Righe:** 225-246  
**Firma:** `def get_entry(self, entry_id: str) -> Entry`  
**Scopo:** Recupera `get_entry`.

**Chiamate dirette osservate nel corpo:** `Entry.from_bytes`, `VaultError`, `_LOG.debug`, `_LOG.info`, `_LOG.warning`, `elapsed_ms`, `len`, `path.exists`, `path.read_bytes`, `self._decrypt`, `self._require_unlocked`, `self._verify_record_binding`, `time.perf_counter`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.resolve_reference_value -->
#### `Vault.resolve_reference_value`

**Tipo:** funzione/metodo  
**Righe:** 248-281  
**Firma:** `def resolve_reference_value(self, value: str | None, *, _stack: tuple[tuple[str, str], ...]=(), _max_depth: int=32) -> str | None`  
**Scopo:** Resolve a KeePassXC-style UUID reference stored as a whole field. Keys NG intentionally implements the UUID subset requested for reusable credentials: {REF:U@I:<UUID>} and {REF:P@I:<UUID>}. References can be chained, but cycles and excessive nesting are rejected.

**Chiamate dirette osservate nel corpo:** `ReferenceError`, `join`, `len`, `parse_entry_reference`, `self.get_entry`, `self.resolve_reference_value`.

**Eccezioni sollevate esplicitamente:** `ReferenceError`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.resolved_username -->
#### `Vault.resolved_username`

**Tipo:** funzione/metodo  
**Righe:** 283-286  
**Firma:** `def resolved_username(self, entry: Entry | str) -> str | None`  
**Scopo:** Implementa l'operazione `resolved_username` in questo modulo.

**Chiamate dirette osservate nel corpo:** `isinstance`, `self.get_entry`, `self.resolve_reference_value`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.resolved_password -->
#### `Vault.resolved_password`

**Tipo:** funzione/metodo  
**Righe:** 288-290  
**Firma:** `def resolved_password(self, entry: Entry | str) -> str | None`  
**Scopo:** Implementa l'operazione `resolved_password` in questo modulo.

**Chiamate dirette osservate nel corpo:** `isinstance`, `self.get_entry`, `self.resolve_reference_value`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.resolved_action -->
#### `Vault.resolved_action`

**Tipo:** funzione/metodo  
**Righe:** 292-298  
**Firma:** `def resolved_action(self, entry: Entry, action: Action) -> Action`  
**Scopo:** Return an action with any UUID-referenced username resolved.

**Chiamate dirette osservate nel corpo:** `replace`, `self.resolve_reference_value`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.delete_entry -->
#### `Vault.delete_entry`

**Tipo:** funzione/metodo  
**Righe:** 300-309  
**Firma:** `def delete_entry(self, entry_id: str) -> None`  
**Scopo:** Elimina `delete_entry`.

**Chiamate dirette osservate nel corpo:** `VaultError`, `path.unlink`, `self._require_unlocked`, `self._write_catalog`, `self.load_catalog`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Attributi oggetto modificati:** `catalog.items`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.list_items -->
#### `Vault.list_items`

**Tipo:** funzione/metodo  
**Righe:** 311-325  
**Firma:** `def list_items(self, folder_id: str | None=None, recursive: bool=False) -> list[CatalogItem]`  
**Scopo:** Restituisce una vista filtrata/elencata di `list_items`.

**Chiamate dirette osservate nel corpo:** `allowed.add`, `self.load_catalog`, `self.load_folders`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._folder_paths_from -->
#### `Vault._folder_paths_from`

**Tipo:** funzione/metodo  
**Righe:** 328-354  
**Firma:** `def _folder_paths_from(folders: list[Folder]) -> dict[str, str]`  
**Scopo:** Build all folder paths in O(n) without repeated vault decryptions.

**Chiamate dirette osservate nel corpo:** `VaultError`, `by_id.get`, `resolve`, `set`, `visiting.add`, `visiting.remove`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 3 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault._folder_paths_from.resolve -->
#### `Vault._folder_paths_from.resolve`

**Tipo:** funzione/metodo  
**Righe:** 333-350  
**Firma:** `def resolve(folder_id: str, visiting: set[str] | None=None) -> str`  
**Scopo:** Implementa l'operazione `resolve` in questo modulo.

**Chiamate dirette osservate nel corpo:** `VaultError`, `by_id.get`, `resolve`, `set`, `visiting.add`, `visiting.remove`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.folder_paths -->
#### `Vault.folder_paths`

**Tipo:** funzione/metodo  
**Righe:** 356-358  
**Firma:** `def folder_paths(self, *, catalog_snapshot: bool=False) -> dict[str, str]`  
**Scopo:** Implementa l'operazione `folder_paths` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self._folder_paths_from`, `self.load_catalog`, `self.load_folders`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.search -->
#### `Vault.search`

**Tipo:** funzione/metodo  
**Righe:** 360-375  
**Firma:** `def search(self, query: str) -> list[CatalogItem]`  
**Scopo:** Implementa l'operazione `search` in questo modulo.

**Chiamate dirette osservate nel corpo:** `casefold`, `folder_names.get`, `join`, `list`, `matches.append`, `query.casefold`, `self._folder_paths_from`, `self.load_catalog`, `strip`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.reindex -->
#### `Vault.reindex`

**Tipo:** funzione/metodo  
**Righe:** 377-387  
**Firma:** `def reindex(self) -> Catalog`  
**Scopo:** Implementa l'operazione `reindex` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Catalog`, `Entry.from_bytes`, `glob`, `items.append`, `list`, `path.read_bytes`, `self._catalog_item`, `self._decrypt`, `self._require_unlocked`, `self._write_catalog`, `self.load_folders`, `sorted`, `x.title.casefold`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem, cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.catalog_health -->
#### `Vault.catalog_health`

**Tipo:** funzione/metodo  
**Righe:** 389-410  
**Firma:** `def catalog_health(self) -> tuple[bool, list[str]]`  
**Scopo:** Implementa l'operazione `catalog_health` in questo modulo.

**Chiamate dirette osservate nel corpo:** `by_id.get`, `glob`, `hexdigest`, `issues.append`, `path.read_bytes`, `self.load_catalog`, `self.load_folders`, `set`, `sha256`, `sorted`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 2 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.list_folders -->
#### `Vault.list_folders`

**Tipo:** funzione/metodo  
**Righe:** 413-416  
**Firma:** `def list_folders(self) -> list[Folder]`  
**Scopo:** Restituisce una vista filtrata/elencata di `list_folders`.

**Chiamate dirette osservate nel corpo:** `casefold`, `list`, `self._folder_paths_from`, `self.load_folders`, `sorted`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.get_folder -->
#### `Vault.get_folder`

**Tipo:** funzione/metodo  
**Righe:** 418-422  
**Firma:** `def get_folder(self, folder_id: str) -> Folder`  
**Scopo:** Recupera `get_folder`.

**Chiamate dirette osservate nel corpo:** `VaultError`, `self.load_folders`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.folder_path -->
#### `Vault.folder_path`

**Tipo:** funzione/metodo  
**Righe:** 424-430  
**Firma:** `def folder_path(self, folder_id: str | None) -> str`  
**Scopo:** Implementa l'operazione `folder_path` in questo modulo.

**Chiamate dirette osservate nel corpo:** `VaultError`, `self.folder_paths`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.resolve_folder_path -->
#### `Vault.resolve_folder_path`

**Tipo:** funzione/metodo  
**Righe:** 432-445  
**Firma:** `def resolve_folder_path(self, path: str) -> str | None`  
**Scopo:** Risolve `resolve_folder_path`.

**Chiamate dirette osservate nel corpo:** `VaultError`, `folder.name.casefold`, `len`, `part.casefold`, `path.replace`, `path.strip`, `self.load_folders`, `split`, `strip`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.create_folder -->
#### `Vault.create_folder`

**Tipo:** funzione/metodo  
**Righe:** 447-462  
**Firma:** `def create_folder(self, name: str, parent_id: str | None=None) -> Folder`  
**Scopo:** Crea `create_folder`.

**Chiamate dirette osservate nel corpo:** `Folder.create`, `VaultError`, `any`, `casefold`, `folder.name.casefold`, `folder.validate`, `name.strip`, `self._require_unlocked`, `self._sync_catalog_folders`, `self._write_catalog`, `self._write_folders`, `self.load_catalog`, `self.load_folders`, `store.folders.append`, `store.validate`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.create_folder_path -->
#### `Vault.create_folder_path`

**Tipo:** funzione/metodo  
**Righe:** 464-478  
**Firma:** `def create_folder_path(self, path: str) -> Folder | None`  
**Scopo:** Crea `create_folder_path`.

**Chiamate dirette osservate nel corpo:** `folder.name.casefold`, `next`, `normalized.replace`, `part.casefold`, `path.strip`, `self.create_folder`, `self.load_folders`, `split`, `strip`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.rename_folder -->
#### `Vault.rename_folder`

**Tipo:** funzione/metodo  
**Righe:** 480-496  
**Firma:** `def rename_folder(self, folder_id: str, new_name: str) -> Folder`  
**Scopo:** Implementa l'operazione `rename_folder` in questo modulo.

**Chiamate dirette osservate nel corpo:** `FolderStore`, `VaultError`, `any`, `new_name.strip`, `next`, `normalized.casefold`, `other.name.casefold`, `replace`, `self._sync_catalog_folders`, `self._write_catalog`, `self._write_folders`, `self.load_catalog`, `self.load_folders`, `store.validate`, `utc_now`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Attributi oggetto modificati:** `folder.name`, `folder.updated_at`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.move_folder -->
#### `Vault.move_folder`

**Tipo:** funzione/metodo  
**Righe:** 498-521  
**Firma:** `def move_folder(self, folder_id: str, parent_id: str | None) -> Folder`  
**Scopo:** Implementa l'operazione `move_folder` in questo modulo.

**Chiamate dirette osservate nel corpo:** `FolderStore`, `VaultError`, `any`, `by_id.get`, `folder.name.casefold`, `other.name.casefold`, `replace`, `self._sync_catalog_folders`, `self._write_catalog`, `self._write_folders`, `self.load_catalog`, `self.load_folders`, `store.validate`, `utc_now`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Attributi oggetto modificati:** `folder.parent_id`, `folder.updated_at`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.delete_folder -->
#### `Vault.delete_folder`

**Tipo:** funzione/metodo  
**Righe:** 523-536  
**Firma:** `def delete_folder(self, folder_id: str) -> None`  
**Scopo:** Elimina `delete_folder`.

**Chiamate dirette osservate nel corpo:** `VaultError`, `any`, `len`, `self._sync_catalog_folders`, `self._write_catalog`, `self._write_folders`, `self.load_catalog`, `self.load_folders`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Attributi oggetto modificati:** `store.folders`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.storage.vault:Vault.move_entry -->
#### `Vault.move_entry`

**Tipo:** funzione/metodo  
**Righe:** 538-544  
**Firma:** `def move_entry(self, entry_id: str, folder_id: str | None) -> Entry`  
**Scopo:** Implementa l'operazione `move_entry` in questo modulo.

**Chiamate dirette osservate nel corpo:** `VaultError`, `self.get_entry`, `self.load_folders`, `self.save_entry`.

**Eccezioni sollevate esplicitamente:** `VaultError`.

**Attributi oggetto modificati:** `entry.folder_id`, `entry.revision`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

### `keys_ng.tui.main`

Interfaccia terminale Textual e relative azioni/scorciatoie.

**Sorgente:** `src/keys_ng/tui/main.py`  
**Simboli eseguibili:** 148

**Dipendenze dirette del modulo:** `__future__`, `argparse`, `keys_ng`, `keys_ng.crypto.factory`, `keys_ng.i18n`, `keys_ng.migration.keepassxc`, `keys_ng.migration.keepassxc_export`, `keys_ng.platform.app_identity`, `keys_ng.services.actions`, `keys_ng.services.clipboard`, `keys_ng.services.diagnostics`, `keys_ng.services.entry_editor`, `keys_ng.services.passwords`, `keys_ng.services.qr`, `keys_ng.services.totp`, `keys_ng.services.trusted_signers`, `keys_ng.services.vault_init`, `keys_ng.services.vault_sessions`, `keys_ng.storage.inbox`, `keys_ng.storage.settings`, `keys_ng.storage.vault`, `pathlib`, `sys`

<!-- symbol:keys_ng.tui.main:main -->
#### `main`

**Tipo:** funzione/metodo  
**Righe:** 32-1437  
**Firma:** `def main() -> None`  
**Scopo:** Implementa l'operazione `main` in questo modulo.

**Chiamate dirette osservate nel corpo:** `AppSettings.load`, `Binding`, `Button`, `Checkbox`, `ChoiceScreen`, `ConfirmScreen`, `EntryDraft`, `EntryDraft.from_entry`, `EntryEditorScreen`, `ExportVaultScreen`, `Footer`, `Header`, `HelpScreen`, `Horizontal`, `InboxScreen`, `Input`, `KeePassXCImportScreen`, `KeysApp`, `Label`, `MoveScreen`, `NameScreen`, `PasswordGeneratorScreen`, `Path`, `Path.cwd`, `Path.home`, `PreferencesScreen`, `Select`, `Static`, `SystemExit`, `TextArea`, `Tree`, `TrustedSignersScreen`, `ValueError`, `Vault`, `VaultCreationApp`, `VaultInitRequest`, `VaultSessionManager`, `VaultStartApp`, `VaultSwitcherScreen`, `Vertical`, `VerticalScroll`, `_`, `__init__`, `_select_value_is_blank`, `add_trusted_signer`, `argparse.ArgumentParser`, `available_vault_keys`, `banner.add_class`, `banner.remove_class`, `banner.update`, `bool`, `build_entry_from_draft`, `build_otpauth_uri`, `ch.isalnum`, `choose_vault`, `configure_diagnostics`, `configure_language`, `copy_secret_cli`, `create_crypto_backend`, `create_vault`, `current_language`, `delete_inbox_item`, `eligible_signing_keys`, `enumerate`, `event.value.strip`, `exists`, `expanduser`, `export_entry_xml`, `export_vault_xml`, `files`, `focus`, `folder_nodes.get`, `folder_options`, `format`, `format_import_report`, `generate_password`, `generate_totp`, `get`, `get_logger`, `getattr`, `import_inbox_item`, `import_keepassxc`, `info`, `inspect_inbox`, `int`, `isinstance`, `join`, `joinpath`, `launch_action`, `len`, `list`, `list_trusted_signers`, `load_text`, `next`, `options.append`, `parent.add`, `parent.add_leaf`, `parse_totp_qr_file`, `parser.add_argument`, `parser.parse_args`, `paths.get`, `pending_inbox_paths`, `print`, `remaining.remove`, `remove_trusted_signer`, `resolve`, `resource.is_file`, `resource.read_text`, `root.joinpath`, `run`, `select.set_options`, `self._activate_opened_vault`, `self._banner_timer.stop`, `self._collect`, `self._copy`, `self._copy_generated`, `self._display_active_vault`, `self._finish_edit_entry`, `self._finish_export_entry`, `self._finish_open_vault`, `self._generate`, `self._load_qr`, `self._refresh_after_mutation`, `self._reset_selection`, `self._run`, `self._show_clipboard_banner`, `self._status`, `self._text`, `self._toggle_password_visibility`, `self._update_command_hints`, `self.action_cancel`, `self.action_close`, `self.action_reload_tree`, `self.action_save`, `self.app.copy_to_clipboard`, `self.app.push_screen`, `self.copy_to_clipboard`, `self.dismiss`, `self.exit`, `self.push_screen`, `self.query_one`, `self.rebuild_tree`, `self.refresh_inbox`, `self.refresh_signers`, `self.selected`, `self.set_timer`, `self.show_item`, `sessions.activate`, `sessions.add`, `sessions.close`, `sessions.contains`, `sessions.lock_all`, `sessions.opened`, `set_textual_terminal_title`, `settings.remember_vault`, `settings.save`, `status.update`, `str`, `strip`, `super`, `tree.clear`, `tree.root.add_leaf`, `tree.root.expand`, `tree.root.set_label`, `type`, `update`, `value.startswith`, `value.strip`, `vault.create_folder`, `vault.crypto.hard_lock`, `vault.delete_entry`, `vault.delete_folder`, `vault.folder_path`, `vault.folder_paths`, `vault.get_entry`, `vault.get_folder`, `vault.list_folders`, `vault.list_items`, `vault.lock`, `vault.move_entry`, `vault.move_folder`, `vault.rename_folder`, `vault.resolved_action`, `vault.resolved_password`, `vault.resolved_username`, `vault.save_entry`, `vault.search`, `vault.unlock`, `write_export`.

**Eccezioni sollevate esplicitamente:** `SystemExit`, `ValueError`.

**Attributi oggetto modificati:** `banner.styles.background`, `banner.styles.color`, `password_input.password`, `select.value`, `self._banner_timer`, `self._inbox_notice_shown`, `self.confirm_label`, `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.current_kind`, `self.destructive`, `self.dialog_title`, `self.draft`, `self.exclude_id`, `self.items`, `self.message`, `self.options`, `self.resource_name`, `self.selected`, `self.title`, `self.title_text`, `self.value`, `settings.auto_lock_timeout`, `settings.clipboard_password_timeout`, `settings.clipboard_totp_timeout`, `settings.diagnostics_enabled`, `settings.gpg_executable`, `settings.gpgconf_executable`, `settings.language`, `settings.tree_startup_view`, `toggle.label`, `value`.

**Forma del flusso di controllo:** 134 blocchi condizionali, 10 cicli, 40 blocchi try, 47 context manager, 69 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process, filesystem, cryptography/key-agent, clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultCreationApp -->
#### `main.VaultCreationApp`

**Tipo:** classe  
**Righe:** 70-133  
**Basi:** `App[str | None]`  
**Metodi:** `compose`, `on_button_pressed`, `action_cancel`  
**Responsabilità:** Standalone keyboard-first onboarding wizard used when no vault is supplied.

<!-- symbol:keys_ng.tui.main:main.VaultCreationApp.compose -->
#### `main.VaultCreationApp.compose`

**Tipo:** funzione/metodo  
**Righe:** 84-104  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Checkbox`, `Horizontal`, `Input`, `Label`, `Path.home`, `Select`, `Static`, `Vertical`, `_`, `available_vault_keys`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultCreationApp.on_button_pressed -->
#### `main.VaultCreationApp.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 106-130  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ValueError`, `VaultInitRequest`, `_`, `bool`, `create_vault`, `self.exit`, `self.query_one`, `str`, `update`, `value.strip`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultCreationApp.action_cancel -->
#### `main.VaultCreationApp.action_cancel`

**Tipo:** funzione/metodo  
**Righe:** 132-133  
**Firma:** `def action_cancel(self) -> None`  
**Scopo:** Implementa l'operazione `action_cancel` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.exit`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultStartApp -->
#### `main.VaultStartApp`

**Tipo:** classe  
**Righe:** 135-160  
**Basi:** `App[str | None]`  
**Metodi:** `compose`, `on_select_changed`, `on_button_pressed`  
**Responsabilità:** Start screen for opening, creating, or selecting a recent vault.

<!-- symbol:keys_ng.tui.main:main.VaultStartApp.compose -->
#### `main.VaultStartApp.compose`

**Tipo:** funzione/metodo  
**Righe:** 142-153  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Input`, `Label`, `Path`, `Path.home`, `Select`, `Static`, `Vertical`, `_`, `exists`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultStartApp.on_select_changed -->
#### `main.VaultStartApp.on_select_changed`

**Tipo:** funzione/metodo  
**Righe:** 154-156  
**Firma:** `def on_select_changed(self, event: Select.Changed) -> None`  
**Scopo:** Implementa l'operazione `on_select_changed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_select_value_is_blank`, `self.query_one`, `str`.

**Attributi oggetto modificati:** `value`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultStartApp.on_button_pressed -->
#### `main.VaultStartApp.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 157-160  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.exit`, `self.query_one`, `value.strip`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.choose_vault -->
#### `main.choose_vault`

**Tipo:** funzione/metodo  
**Righe:** 162-179  
**Firma:** `def choose_vault(path: str | None=None) -> str | None`  
**Scopo:** Implementa l'operazione `choose_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Path`, `VaultCreationApp`, `VaultStartApp`, `expanduser`, `resolve`, `run`, `settings.remember_vault`, `settings.save`, `str`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 1 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.folder_options -->
#### `main.folder_options`

**Tipo:** funzione/metodo  
**Righe:** 187-192  
**Firma:** `def folder_options(exclude_id: str | None=None) -> list[tuple[str, str]]`  
**Scopo:** Implementa l'operazione `folder_options` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `options.append`, `vault.folder_path`, `vault.list_folders`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen -->
#### `main.PasswordGeneratorScreen`

**Tipo:** classe  
**Righe:** 194-251  
**Basi:** `ModalScreen[str | None]`  
**Metodi:** `compose`, `on_mount`, `_generate`, `_copy_generated`, `on_button_pressed`, `action_cancel`  
**Responsabilità:** Implementa l'operazione `PasswordGeneratorScreen` in questo modulo.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen.compose -->
#### `main.PasswordGeneratorScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 201-216  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Checkbox`, `Horizontal`, `Input`, `Label`, `Static`, `Vertical`, `_`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen.on_mount -->
#### `main.PasswordGeneratorScreen.on_mount`

**Tipo:** funzione/metodo  
**Righe:** 217-217  
**Firma:** `def on_mount(self) -> None`  
**Scopo:** Implementa l'operazione `on_mount` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self._generate`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen._generate -->
#### `main.PasswordGeneratorScreen._generate`

**Tipo:** funzione/metodo  
**Righe:** 218-230  
**Firma:** `def _generate(self) -> None`  
**Scopo:** Helper interno che implementa `_generate`.

**Chiamate dirette osservate nel corpo:** `_`, `generate_password`, `int`, `self.query_one`.

**Attributi oggetto modificati:** `value`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen._copy_generated -->
#### `main.PasswordGeneratorScreen._copy_generated`

**Tipo:** funzione/metodo  
**Righe:** 231-244  
**Firma:** `def _copy_generated(self) -> None`  
**Scopo:** Helper interno che implementa `_copy_generated`.

**Chiamate dirette osservate nel corpo:** `_`, `copy_secret_cli`, `self.app.copy_to_clipboard`, `self.query_one`, `status.update`, `type`, `value.startswith`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen.on_button_pressed -->
#### `main.PasswordGeneratorScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 246-250  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self._copy_generated`, `self._generate`, `self.dismiss`, `self.query_one`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.PasswordGeneratorScreen.action_cancel -->
#### `main.PasswordGeneratorScreen.action_cancel`

**Tipo:** funzione/metodo  
**Righe:** 251-251  
**Firma:** `def action_cancel(self) -> None`  
**Scopo:** Implementa l'operazione `action_cancel` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen -->
#### `main.KeePassXCImportScreen`

**Tipo:** classe  
**Righe:** 253-292  
**Basi:** `ModalScreen[bool]`  
**Metodi:** `compose`, `_run`, `on_button_pressed`, `action_close`  
**Responsabilità:** Implementa l'operazione `KeePassXCImportScreen` in questo modulo.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen.compose -->
#### `main.KeePassXCImportScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 261-273  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Checkbox`, `Horizontal`, `Input`, `Label`, `Static`, `TextArea`, `Vertical`, `_`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen._run -->
#### `main.KeePassXCImportScreen._run`

**Tipo:** funzione/metodo  
**Righe:** 274-283  
**Firma:** `def _run(self, dry_run: bool)`  
**Scopo:** Helper interno che implementa `_run`.

**Chiamate dirette osservate nel corpo:** `ValueError`, `_`, `import_keepassxc`, `self.query_one`, `value.strip`.

**Eccezioni sollevate esplicitamente:** `ValueError`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen.on_button_pressed -->
#### `main.KeePassXCImportScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 284-291  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `format_import_report`, `load_text`, `self._run`, `self.dismiss`, `self.query_one`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** process.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeePassXCImportScreen.action_close -->
#### `main.KeePassXCImportScreen.action_close`

**Tipo:** funzione/metodo  
**Righe:** 292-292  
**Firma:** `def action_close(self) -> None`  
**Scopo:** Implementa l'operazione `action_close` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ExportVaultScreen -->
#### `main.ExportVaultScreen`

**Tipo:** classe  
**Righe:** 294-306  
**Basi:** `ModalScreen[str | None]`  
**Metodi:** `compose`, `on_button_pressed`  
**Responsabilità:** Implementa l'operazione `ExportVaultScreen` in questo modulo.

<!-- symbol:keys_ng.tui.main:main.ExportVaultScreen.compose -->
#### `main.ExportVaultScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 296-304  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Input`, `Path.cwd`, `Static`, `Vertical`, `_`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ExportVaultScreen.on_button_pressed -->
#### `main.ExportVaultScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 305-306  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`, `self.query_one`, `value.strip`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.PreferencesScreen -->
#### `main.PreferencesScreen`

**Tipo:** classe  
**Righe:** 308-336  
**Basi:** `ModalScreen[bool]`  
**Metodi:** `compose`, `on_button_pressed`  
**Responsabilità:** Implementa l'operazione `PreferencesScreen` in questo modulo.

<!-- symbol:keys_ng.tui.main:main.PreferencesScreen.compose -->
#### `main.PreferencesScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 310-323  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Checkbox`, `Horizontal`, `Input`, `Label`, `Select`, `Static`, `Vertical`, `VerticalScroll`, `_`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 3 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.PreferencesScreen.on_button_pressed -->
#### `main.PreferencesScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 324-336  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `int`, `self.dismiss`, `self.query_one`, `settings.save`, `str`, `value.strip`.

**Attributi oggetto modificati:** `settings.auto_lock_timeout`, `settings.clipboard_password_timeout`, `settings.clipboard_totp_timeout`, `settings.diagnostics_enabled`, `settings.gpg_executable`, `settings.gpgconf_executable`, `settings.language`, `settings.tree_startup_view`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.HelpScreen -->
#### `main.HelpScreen`

**Tipo:** classe  
**Righe:** 338-356  
**Basi:** `ModalScreen[None]`  
**Metodi:** `__init__`, `_text`, `compose`, `on_button_pressed`  
**Responsabilità:** Implementa l'operazione `HelpScreen` in questo modulo.

<!-- symbol:keys_ng.tui.main:main.HelpScreen.__init__ -->
#### `main.HelpScreen.__init__`

**Tipo:** funzione/metodo  
**Righe:** 340-341  
**Firma:** `def __init__(self, resource_name: str='README.md') -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `__init__`, `super`.

**Attributi oggetto modificati:** `self.resource_name`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.HelpScreen._text -->
#### `main.HelpScreen._text`

**Tipo:** funzione/metodo  
**Righe:** 342-351  
**Firma:** `def _text(self) -> str`  
**Scopo:** Helper interno che implementa `_text`.

**Chiamate dirette osservate nel corpo:** `_`, `current_language`, `files`, `joinpath`, `resource.is_file`, `resource.read_text`, `root.joinpath`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.HelpScreen.compose -->
#### `main.HelpScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 352-355  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `TextArea`, `Vertical`, `_`, `self._text`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 1 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.HelpScreen.on_button_pressed -->
#### `main.HelpScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 356-356  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen -->
#### `main.EntryEditorScreen`

**Tipo:** classe  
**Righe:** 358-515  
**Basi:** `ModalScreen[EntryDraft | None]`  
**Metodi:** `__init__`, `compose`, `_collect`, `action_save`, `action_cancel`, `_finish_generated_password`, `_toggle_password_visibility`, `_load_qr`, `on_button_pressed`  
**Responsabilità:** Keyboard-first full editor shared semantically with the GUI editor.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.__init__ -->
#### `main.EntryEditorScreen.__init__`

**Tipo:** funzione/metodo  
**Righe:** 378-381  
**Firma:** `def __init__(self, draft: EntryDraft, title: str) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `__init__`, `super`.

**Attributi oggetto modificati:** `self.dialog_title`, `self.draft`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.compose -->
#### `main.EntryEditorScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 383-455  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Input`, `Label`, `Select`, `Static`, `TextArea`, `Vertical`, `VerticalScroll`, `_`, `folder_options`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 17 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen._collect -->
#### `main.EntryEditorScreen._collect`

**Tipo:** funzione/metodo  
**Righe:** 457-474  
**Firma:** `def _collect(self) -> EntryDraft`  
**Scopo:** Helper interno che implementa `_collect`.

**Chiamate dirette osservate nel corpo:** `EntryDraft`, `self.query_one`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.action_save -->
#### `main.EntryEditorScreen.action_save`

**Tipo:** funzione/metodo  
**Righe:** 476-477  
**Firma:** `def action_save(self) -> None`  
**Scopo:** Implementa l'operazione `action_save` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self._collect`, `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.action_cancel -->
#### `main.EntryEditorScreen.action_cancel`

**Tipo:** funzione/metodo  
**Righe:** 479-480  
**Firma:** `def action_cancel(self) -> None`  
**Scopo:** Implementa l'operazione `action_cancel` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen._finish_generated_password -->
#### `main.EntryEditorScreen._finish_generated_password`

**Tipo:** funzione/metodo  
**Righe:** 482-484  
**Firma:** `def _finish_generated_password(self, value: str | None) -> None`  
**Scopo:** Helper interno che implementa `_finish_generated_password`.

**Chiamate dirette osservate nel corpo:** `self.query_one`.

**Attributi oggetto modificati:** `value`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen._toggle_password_visibility -->
#### `main.EntryEditorScreen._toggle_password_visibility`

**Tipo:** funzione/metodo  
**Righe:** 486-490  
**Firma:** `def _toggle_password_visibility(self) -> None`  
**Scopo:** Helper interno che implementa `_toggle_password_visibility`.

**Chiamate dirette osservate nel corpo:** `_`, `self.query_one`.

**Attributi oggetto modificati:** `password_input.password`, `toggle.label`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen._load_qr -->
#### `main.EntryEditorScreen._load_qr`

**Tipo:** funzione/metodo  
**Righe:** 492-503  
**Firma:** `def _load_qr(self) -> None`  
**Scopo:** Helper interno che implementa `_load_qr`.

**Chiamate dirette osservate nel corpo:** `_`, `build_otpauth_uri`, `parse_totp_qr_file`, `self.query_one`, `update`, `value.strip`.

**Attributi oggetto modificati:** `value`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.EntryEditorScreen.on_button_pressed -->
#### `main.EntryEditorScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 505-515  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `PasswordGeneratorScreen`, `self._load_qr`, `self._toggle_password_visibility`, `self.action_cancel`, `self.action_save`, `self.app.push_screen`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.NameScreen -->
#### `main.NameScreen`

**Tipo:** classe  
**Righe:** 517-548  
**Basi:** `ModalScreen[str | None]`  
**Metodi:** `__init__`, `compose`, `action_save`, `action_cancel`, `on_button_pressed`  
**Responsabilità:** Small modal used for folder creation and rename.

<!-- symbol:keys_ng.tui.main:main.NameScreen.__init__ -->
#### `main.NameScreen.__init__`

**Tipo:** funzione/metodo  
**Righe:** 527-530  
**Firma:** `def __init__(self, title: str, value: str='') -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `__init__`, `super`.

**Attributi oggetto modificati:** `self.dialog_title`, `self.value`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.NameScreen.compose -->
#### `main.NameScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 532-538  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Input`, `Static`, `Vertical`, `_`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.NameScreen.action_save -->
#### `main.NameScreen.action_save`

**Tipo:** funzione/metodo  
**Righe:** 540-542  
**Firma:** `def action_save(self) -> None`  
**Scopo:** Implementa l'operazione `action_save` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`, `self.query_one`, `value.strip`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.NameScreen.action_cancel -->
#### `main.NameScreen.action_cancel`

**Tipo:** funzione/metodo  
**Righe:** 544-545  
**Firma:** `def action_cancel(self) -> None`  
**Scopo:** Implementa l'operazione `action_cancel` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.NameScreen.on_button_pressed -->
#### `main.NameScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 547-548  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.action_cancel`, `self.action_save`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.MoveScreen -->
#### `main.MoveScreen`

**Tipo:** classe  
**Righe:** 550-582  
**Basi:** `ModalScreen[str | None | bool]`  
**Metodi:** `__init__`, `compose`, `action_save`, `action_cancel`, `on_button_pressed`  
**Responsabilità:** Choose a destination folder. False means cancelled; None means root.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.__init__ -->
#### `main.MoveScreen.__init__`

**Tipo:** funzione/metodo  
**Righe:** 560-564  
**Firma:** `def __init__(self, title: str, selected: str | None, exclude_id: str | None=None) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `__init__`, `super`.

**Attributi oggetto modificati:** `self.dialog_title`, `self.exclude_id`, `self.selected`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.compose -->
#### `main.MoveScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 566-572  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`, `folder_options`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.action_save -->
#### `main.MoveScreen.action_save`

**Tipo:** funzione/metodo  
**Righe:** 574-576  
**Firma:** `def action_save(self) -> None`  
**Scopo:** Implementa l'operazione `action_save` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`, `self.query_one`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.action_cancel -->
#### `main.MoveScreen.action_cancel`

**Tipo:** funzione/metodo  
**Righe:** 578-579  
**Firma:** `def action_cancel(self) -> None`  
**Scopo:** Implementa l'operazione `action_cancel` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.MoveScreen.on_button_pressed -->
#### `main.MoveScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 581-582  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.action_cancel`, `self.action_save`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen -->
#### `main.ConfirmScreen`

**Tipo:** classe  
**Righe:** 584-611  
**Basi:** `ModalScreen[bool]`  
**Metodi:** `__init__`, `compose`, `action_no`, `on_button_pressed`  
**Responsabilità:** Explicit confirmation screen for destructive and sensitive actions.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen.__init__ -->
#### `main.ConfirmScreen.__init__`

**Tipo:** funzione/metodo  
**Righe:** 594-598  
**Firma:** `def __init__(self, message: str, confirm_label: str | None=None, *, destructive: bool=False) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `_`, `__init__`, `super`.

**Attributi oggetto modificati:** `self.confirm_label`, `self.destructive`, `self.message`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen.compose -->
#### `main.ConfirmScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 600-605  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Static`, `Vertical`, `_`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen.action_no -->
#### `main.ConfirmScreen.action_no`

**Tipo:** funzione/metodo  
**Righe:** 607-608  
**Firma:** `def action_no(self) -> None`  
**Scopo:** Implementa l'operazione `action_no` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ConfirmScreen.on_button_pressed -->
#### `main.ConfirmScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 610-611  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen -->
#### `main.TrustedSignersScreen`

**Tipo:** classe  
**Righe:** 613-680  
**Basi:** `ModalScreen[None]`  
**Metodi:** `compose`, `on_mount`, `refresh_signers`, `action_close`, `on_select_changed`, `_finish_add`, `_finish_remove`, `on_button_pressed`  
**Responsabilità:** Implementa l'operazione `TrustedSignersScreen` in questo modulo.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.compose -->
#### `main.TrustedSignersScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 621-630  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.on_mount -->
#### `main.TrustedSignersScreen.on_mount`

**Tipo:** funzione/metodo  
**Righe:** 632-633  
**Firma:** `def on_mount(self) -> None`  
**Scopo:** Implementa l'operazione `on_mount` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.refresh_signers`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.refresh_signers -->
#### `main.TrustedSignersScreen.refresh_signers`

**Tipo:** funzione/metodo  
**Righe:** 635-643  
**Firma:** `def refresh_signers(self) -> None`  
**Scopo:** Implementa l'operazione `refresh_signers` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `list_trusted_signers`, `select.set_options`, `self.query_one`, `update`.

**Attributi oggetto modificati:** `select.value`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.action_close -->
#### `main.TrustedSignersScreen.action_close`

**Tipo:** funzione/metodo  
**Righe:** 645-646  
**Firma:** `def action_close(self) -> None`  
**Scopo:** Implementa l'operazione `action_close` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.on_select_changed -->
#### `main.TrustedSignersScreen.on_select_changed`

**Tipo:** funzione/metodo  
**Righe:** 648-650  
**Firma:** `def on_select_changed(self, event: Select.Changed) -> None`  
**Scopo:** Implementa l'operazione `on_select_changed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_select_value_is_blank`, `self.query_one`, `str`, `update`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen._finish_add -->
#### `main.TrustedSignersScreen._finish_add`

**Tipo:** funzione/metodo  
**Righe:** 652-658  
**Firma:** `def _finish_add(self, value) -> None`  
**Scopo:** Helper interno che implementa `_finish_add`.

**Chiamate dirette osservate nel corpo:** `_`, `add_trusted_signer`, `self.query_one`, `self.refresh_signers`, `str`, `update`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen._finish_remove -->
#### `main.TrustedSignersScreen._finish_remove`

**Tipo:** funzione/metodo  
**Righe:** 660-667  
**Firma:** `def _finish_remove(self, confirmed: bool) -> None`  
**Scopo:** Helper interno che implementa `_finish_remove`.

**Chiamate dirette osservate nel corpo:** `_`, `_select_value_is_blank`, `remove_trusted_signer`, `self.query_one`, `self.refresh_signers`, `str`, `update`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.TrustedSignersScreen.on_button_pressed -->
#### `main.TrustedSignersScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 669-680  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ChoiceScreen`, `ConfirmScreen`, `_`, `_select_value_is_blank`, `eligible_signing_keys`, `list_trusted_signers`, `self.action_close`, `self.app.push_screen`, `self.query_one`, `update`.

**Forma del flusso di controllo:** 5 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ChoiceScreen -->
#### `main.ChoiceScreen`

**Tipo:** classe  
**Righe:** 683-700  
**Basi:** `ModalScreen[str | bool]`  
**Metodi:** `__init__`, `compose`, `on_button_pressed`  
**Responsabilità:** Implementa l'operazione `ChoiceScreen` in questo modulo.

<!-- symbol:keys_ng.tui.main:main.ChoiceScreen.__init__ -->
#### `main.ChoiceScreen.__init__`

**Tipo:** funzione/metodo  
**Righe:** 689-690  
**Firma:** `def __init__(self, title: str, options) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `__init__`, `super`.

**Attributi oggetto modificati:** `self.options`, `self.title_text`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ChoiceScreen.compose -->
#### `main.ChoiceScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 691-697  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.ChoiceScreen.on_button_pressed -->
#### `main.ChoiceScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 698-700  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`, `self.query_one`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen -->
#### `main.InboxScreen`

**Tipo:** classe  
**Righe:** 703-788  
**Basi:** `ModalScreen[None]`  
**Metodi:** `__init__`, `compose`, `on_mount`, `action_close`, `_status`, `refresh_inbox`, `show_item`, `selected`, `on_select_changed`, `_finish_unsigned`, `_finish_delete`, `on_button_pressed`  
**Responsabilità:** Implementa l'operazione `InboxScreen` in questo modulo.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.__init__ -->
#### `main.InboxScreen.__init__`

**Tipo:** funzione/metodo  
**Righe:** 711-712  
**Firma:** `def __init__(self) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `__init__`, `super`.

**Attributi oggetto modificati:** `self.items`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.compose -->
#### `main.InboxScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 713-724  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.on_mount -->
#### `main.InboxScreen.on_mount`

**Tipo:** funzione/metodo  
**Righe:** 725-725  
**Firma:** `def on_mount(self) -> None`  
**Scopo:** Implementa l'operazione `on_mount` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.refresh_inbox`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.action_close -->
#### `main.InboxScreen.action_close`

**Tipo:** funzione/metodo  
**Righe:** 726-726  
**Firma:** `def action_close(self) -> None`  
**Scopo:** Implementa l'operazione `action_close` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen._status -->
#### `main.InboxScreen._status`

**Tipo:** funzione/metodo  
**Righe:** 727-728  
**Firma:** `def _status(self, item) -> str`  
**Scopo:** Helper interno che implementa `_status`.

**Chiamate dirette osservate nel corpo:** `_`, `get`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.refresh_inbox -->
#### `main.InboxScreen.refresh_inbox`

**Tipo:** funzione/metodo  
**Righe:** 729-740  
**Firma:** `def refresh_inbox(self) -> None`  
**Scopo:** Implementa l'operazione `refresh_inbox` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `enumerate`, `inspect_inbox`, `options.append`, `select.set_options`, `self._status`, `self.query_one`, `self.show_item`, `str`, `update`.

**Attributi oggetto modificati:** `select.value`, `self.items`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 1 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.show_item -->
#### `main.InboxScreen.show_item`

**Tipo:** funzione/metodo  
**Righe:** 741-746  
**Firma:** `def show_item(self, idx: int) -> None`  
**Scopo:** Implementa l'operazione `show_item` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `self._status`, `self.query_one`, `update`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.selected -->
#### `main.InboxScreen.selected`

**Tipo:** funzione/metodo  
**Righe:** 747-750  
**Firma:** `def selected(self)`  
**Scopo:** Implementa l'operazione `selected` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_select_value_is_blank`, `int`, `len`, `self.query_one`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.on_select_changed -->
#### `main.InboxScreen.on_select_changed`

**Tipo:** funzione/metodo  
**Righe:** 751-752  
**Firma:** `def on_select_changed(self, event: Select.Changed) -> None`  
**Scopo:** Implementa l'operazione `on_select_changed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_select_value_is_blank`, `int`, `self.show_item`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen._finish_unsigned -->
#### `main.InboxScreen._finish_unsigned`

**Tipo:** funzione/metodo  
**Righe:** 753-758  
**Firma:** `def _finish_unsigned(self, confirmed: bool) -> None`  
**Scopo:** Helper interno che implementa `_finish_unsigned`.

**Chiamate dirette osservate nel corpo:** `_`, `import_inbox_item`, `self.query_one`, `self.refresh_inbox`, `self.selected`, `update`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen._finish_delete -->
#### `main.InboxScreen._finish_delete`

**Tipo:** funzione/metodo  
**Righe:** 759-764  
**Firma:** `def _finish_delete(self, confirmed: bool) -> None`  
**Scopo:** Helper interno che implementa `_finish_delete`.

**Chiamate dirette osservate nel corpo:** `_`, `delete_inbox_item`, `self.query_one`, `self.refresh_inbox`, `self.selected`, `update`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.InboxScreen.on_button_pressed -->
#### `main.InboxScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 765-788  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ConfirmScreen`, `_`, `add_trusted_signer`, `import_inbox_item`, `list`, `self.action_close`, `self.app.push_screen`, `self.query_one`, `self.refresh_inbox`, `self.selected`, `update`.

**Forma del flusso di controllo:** 10 blocchi condizionali, 1 cicli, 3 blocchi try, 0 context manager, 5 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultSwitcherScreen -->
#### `main.VaultSwitcherScreen`

**Tipo:** classe  
**Righe:** 790-828  
**Basi:** `ModalScreen[tuple[str, str | None] | None]`  
**Metodi:** `compose`, `action_cancel`, `on_button_pressed`  
**Responsabilità:** Select, activate, or close one of the vaults already open in the TUI.

<!-- symbol:keys_ng.tui.main:main.VaultSwitcherScreen.compose -->
#### `main.VaultSwitcherScreen.compose`

**Tipo:** funzione/metodo  
**Righe:** 800-813  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Button`, `Horizontal`, `Select`, `Static`, `Vertical`, `_`, `options.append`, `sessions.opened`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 1 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultSwitcherScreen.action_cancel -->
#### `main.VaultSwitcherScreen.action_cancel`

**Tipo:** funzione/metodo  
**Righe:** 815-816  
**Firma:** `def action_cancel(self) -> None`  
**Scopo:** Implementa l'operazione `action_cancel` in questo modulo.

**Chiamate dirette osservate nel corpo:** `self.dismiss`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.VaultSwitcherScreen.on_button_pressed -->
#### `main.VaultSwitcherScreen.on_button_pressed`

**Tipo:** funzione/metodo  
**Righe:** 818-828  
**Firma:** `def on_button_pressed(self, event: Button.Pressed) -> None`  
**Scopo:** Implementa l'operazione `on_button_pressed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_select_value_is_blank`, `self.dismiss`, `self.query_one`, `str`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp -->
#### `main.KeysApp`

**Tipo:** classe  
**Righe:** 830-1417  
**Basi:** `App`  
**Metodi:** `__init__`, `compose`, `on_mount`, `rebuild_tree`, `_reset_selection`, `_refresh_after_mutation`, `on_input_changed`, `on_tree_node_selected`, `_status`, `_show_clipboard_banner`, `_hide_clipboard_banner`, `_update_command_hints`, `action_focus_search`, `action_reload_tree`, `action_import_keepassxc`, `action_export_vault`, `_finish_export_vault`, `_display_active_vault`, `_activate_opened_vault`, `action_open_vault`, `_finish_open_vault`, `action_recent_vault`, `_finish_recent_vault`, `action_switch_vault`, `_finish_switch_vault`, `action_close_vault`, `action_preferences`, `action_help`, `action_shortcut_help`, `_finish_help`, `action_inbox`, `action_trusted_signers`, `_copy`, `action_copy_url`, `action_copy_uuid`, `action_copy_username`, `action_copy_password`, `action_copy_notes`, `action_copy_totp`, `action_open_action`, `action_new_entry`, `_finish_new_entry`, `action_edit_selected`, `_finish_edit_entry`, `action_new_folder`, `_finish_new_folder`, `_finish_rename_folder`, `action_move_selected`, `_finish_move`, `action_delete_selected`, `_finish_delete`, `action_export_entry`, `_finish_export_entry`, `action_lock_vault`, `action_hard_lock_vault`, `action_unlock_vault`  
**Responsabilità:** Applicazione Textual principale per un vault.

<!-- symbol:keys_ng.tui.main:main.KeysApp.__init__ -->
#### `main.KeysApp.__init__`

**Tipo:** funzione/metodo  
**Righe:** 878-885  
**Firma:** `def __init__(self) -> None`  
**Scopo:** Helper interno che implementa `__init__`.

**Chiamate dirette osservate nel corpo:** `__init__`, `super`.

**Attributi oggetto modificati:** `self._banner_timer`, `self._inbox_notice_shown`, `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.current_kind`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.compose -->
#### `main.KeysApp.compose`

**Tipo:** funzione/metodo  
**Righe:** 887-897  
**Firma:** `def compose(self) -> ComposeResult`  
**Scopo:** Implementa l'operazione `compose` in questo modulo.

**Chiamate dirette osservate nel corpo:** `Footer`, `Header`, `Horizontal`, `Input`, `Static`, `Tree`, `Vertical`, `_`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 2 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.on_mount -->
#### `main.KeysApp.on_mount`

**Tipo:** funzione/metodo  
**Righe:** 899-907  
**Firma:** `def on_mount(self) -> None`  
**Scopo:** Implementa l'operazione `on_mount` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `focus`, `format`, `len`, `pending_inbox_paths`, `self._status`, `self._update_command_hints`, `self.query_one`, `self.rebuild_tree`, `set_textual_terminal_title`.

**Attributi oggetto modificati:** `self._inbox_notice_shown`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.rebuild_tree -->
#### `main.KeysApp.rebuild_tree`

**Tipo:** funzione/metodo  
**Righe:** 909-941  
**Firma:** `def rebuild_tree(self, query: str='') -> None`  
**Scopo:** Implementa l'operazione `rebuild_tree` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `folder_nodes.get`, `list`, `parent.add`, `parent.add_leaf`, `paths.get`, `remaining.remove`, `self.query_one`, `tree.clear`, `tree.root.add_leaf`, `tree.root.expand`, `tree.root.set_label`, `vault.folder_paths`, `vault.list_folders`, `vault.list_items`, `vault.search`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 4 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._reset_selection -->
#### `main.KeysApp._reset_selection`

**Tipo:** funzione/metodo  
**Righe:** 943-949  
**Firma:** `def _reset_selection(self) -> None`  
**Scopo:** Helper interno che implementa `_reset_selection`.

**Chiamate dirette osservate nel corpo:** `_`, `self._update_command_hints`, `self.query_one`, `update`.

**Attributi oggetto modificati:** `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.current_kind`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._refresh_after_mutation -->
#### `main.KeysApp._refresh_after_mutation`

**Tipo:** funzione/metodo  
**Righe:** 951-955  
**Firma:** `def _refresh_after_mutation(self, message: str) -> None`  
**Scopo:** Helper interno che implementa `_refresh_after_mutation`.

**Chiamate dirette osservate nel corpo:** `focus`, `self._reset_selection`, `self._status`, `self.query_one`, `self.rebuild_tree`, `value.strip`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.on_input_changed -->
#### `main.KeysApp.on_input_changed`

**Tipo:** funzione/metodo  
**Righe:** 957-967  
**Firma:** `def on_input_changed(self, event: Input.Changed) -> None`  
**Scopo:** Implementa l'operazione `on_input_changed` in questo modulo.

**Chiamate dirette osservate nel corpo:** `event.value.strip`, `self._reset_selection`, `self.rebuild_tree`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.on_tree_node_selected -->
#### `main.KeysApp.on_tree_node_selected`

**Tipo:** funzione/metodo  
**Righe:** 969-1011  
**Firma:** `def on_tree_node_selected(self, event: Tree.NodeSelected) -> None`  
**Scopo:** Implementa l'operazione `on_tree_node_selected` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `join`, `self._status`, `self._update_command_hints`, `self.query_one`, `update`, `vault.folder_path`, `vault.get_entry`, `vault.get_folder`, `vault.resolved_username`.

**Attributi oggetto modificati:** `self.current_entry`, `self.current_folder_id`, `self.current_id`, `self.current_kind`.

**Forma del flusso di controllo:** 4 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._status -->
#### `main.KeysApp._status`

**Tipo:** funzione/metodo  
**Righe:** 1013-1014  
**Firma:** `def _status(self, text: str) -> None`  
**Scopo:** Helper interno che implementa `_status`.

**Chiamate dirette osservate nel corpo:** `self.query_one`, `update`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._show_clipboard_banner -->
#### `main.KeysApp._show_clipboard_banner`

**Tipo:** funzione/metodo  
**Righe:** 1016-1033  
**Firma:** `def _show_clipboard_banner(self, text: str, level: str='success') -> None`  
**Scopo:** Helper interno che implementa `_show_clipboard_banner`.

**Chiamate dirette osservate nel corpo:** `banner.add_class`, `banner.remove_class`, `banner.update`, `self._banner_timer.stop`, `self.query_one`, `self.set_timer`.

**Attributi oggetto modificati:** `banner.styles.background`, `banner.styles.color`, `self._banner_timer`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._hide_clipboard_banner -->
#### `main.KeysApp._hide_clipboard_banner`

**Tipo:** funzione/metodo  
**Righe:** 1035-1037  
**Firma:** `def _hide_clipboard_banner(self) -> None`  
**Scopo:** Helper interno che implementa `_hide_clipboard_banner`.

**Chiamate dirette osservate nel corpo:** `banner.remove_class`, `self.query_one`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._update_command_hints -->
#### `main.KeysApp._update_command_hints`

**Tipo:** funzione/metodo  
**Righe:** 1039-1047  
**Firma:** `def _update_command_hints(self) -> None`  
**Scopo:** Helper interno che implementa `_update_command_hints`.

**Chiamate dirette osservate nel corpo:** `_`, `self.query_one`, `update`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_focus_search -->
#### `main.KeysApp.action_focus_search`

**Tipo:** funzione/metodo  
**Righe:** 1049-1050  
**Firma:** `def action_focus_search(self) -> None`  
**Scopo:** Implementa l'operazione `action_focus_search` in questo modulo.

**Chiamate dirette osservate nel corpo:** `focus`, `self.query_one`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_reload_tree -->
#### `main.KeysApp.action_reload_tree`

**Tipo:** funzione/metodo  
**Righe:** 1052-1056  
**Firma:** `def action_reload_tree(self) -> None`  
**Scopo:** Implementa l'operazione `action_reload_tree` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `format`, `len`, `pending_inbox_paths`, `self._status`, `self.query_one`, `self.rebuild_tree`, `value.strip`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_import_keepassxc -->
#### `main.KeysApp.action_import_keepassxc`

**Tipo:** funzione/metodo  
**Righe:** 1058-1061  
**Firma:** `def action_import_keepassxc(self) -> None`  
**Scopo:** Implementa l'operazione `action_import_keepassxc` in questo modulo.

**Chiamate dirette osservate nel corpo:** `KeePassXCImportScreen`, `_`, `self._refresh_after_mutation`, `self._status`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_export_vault -->
#### `main.KeysApp.action_export_vault`

**Tipo:** funzione/metodo  
**Righe:** 1063-1065  
**Firma:** `def action_export_vault(self) -> None`  
**Scopo:** Implementa l'operazione `action_export_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ExportVaultScreen`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_export_vault -->
#### `main.KeysApp._finish_export_vault`

**Tipo:** funzione/metodo  
**Righe:** 1067-1072  
**Firma:** `def _finish_export_vault(self, destination: str | None) -> None`  
**Scopo:** Helper interno che implementa `_finish_export_vault`.

**Chiamate dirette osservate nel corpo:** `_`, `export_vault_xml`, `format`, `self._status`, `write_export`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._display_active_vault -->
#### `main.KeysApp._display_active_vault`

**Tipo:** funzione/metodo  
**Righe:** 1074-1093  
**Firma:** `def _display_active_vault(self, message: str | None=None) -> None`  
**Scopo:** Refresh the main widgets after the active vault changes.

**Chiamate dirette osservate nel corpo:** `_`, `focus`, `format`, `self._reset_selection`, `self._status`, `self._update_command_hints`, `self.query_one`, `self.rebuild_tree`, `tree.clear`, `tree.root.expand`, `tree.root.set_label`, `update`.

**Attributi oggetto modificati:** `self.title`, `value`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._activate_opened_vault -->
#### `main.KeysApp._activate_opened_vault`

**Tipo:** funzione/metodo  
**Righe:** 1095-1101  
**Firma:** `def _activate_opened_vault(self, path: str) -> None`  
**Scopo:** Helper interno che implementa `_activate_opened_vault`.

**Chiamate dirette osservate nel corpo:** `_`, `format`, `self._display_active_vault`, `self._status`, `sessions.activate`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_open_vault -->
#### `main.KeysApp.action_open_vault`

**Tipo:** funzione/metodo  
**Righe:** 1103-1104  
**Firma:** `def action_open_vault(self) -> None`  
**Scopo:** Implementa l'operazione `action_open_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `NameScreen`, `Path.home`, `_`, `self.push_screen`, `str`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_open_vault -->
#### `main.KeysApp._finish_open_vault`

**Tipo:** funzione/metodo  
**Righe:** 1106-1123  
**Firma:** `def _finish_open_vault(self, path: str | None) -> None`  
**Scopo:** Helper interno che implementa `_finish_open_vault`.

**Chiamate dirette osservate nel corpo:** `Path`, `Vault`, `_`, `expanduser`, `format`, `resolve`, `self._display_active_vault`, `self._status`, `sessions.activate`, `sessions.add`, `sessions.contains`, `settings.remember_vault`, `settings.save`, `str`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_recent_vault -->
#### `main.KeysApp.action_recent_vault`

**Tipo:** funzione/metodo  
**Righe:** 1125-1130  
**Firma:** `def action_recent_vault(self) -> None`  
**Scopo:** Implementa l'operazione `action_recent_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ChoiceScreen`, `Path`, `_`, `exists`, `resolve`, `self._status`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_recent_vault -->
#### `main.KeysApp._finish_recent_vault`

**Tipo:** funzione/metodo  
**Righe:** 1132-1134  
**Firma:** `def _finish_recent_vault(self, path) -> None`  
**Scopo:** Helper interno che implementa `_finish_recent_vault`.

**Chiamate dirette osservate nel corpo:** `self._finish_open_vault`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_switch_vault -->
#### `main.KeysApp.action_switch_vault`

**Tipo:** funzione/metodo  
**Righe:** 1136-1140  
**Firma:** `def action_switch_vault(self) -> None`  
**Scopo:** Implementa l'operazione `action_switch_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `VaultSwitcherScreen`, `_`, `len`, `self._status`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_switch_vault -->
#### `main.KeysApp._finish_switch_vault`

**Tipo:** funzione/metodo  
**Righe:** 1142-1165  
**Firma:** `def _finish_switch_vault(self, result: tuple[str, str | None] | None) -> None`  
**Scopo:** Helper interno che implementa `_finish_switch_vault`.

**Chiamate dirette osservate nel corpo:** `Path`, `_`, `expanduser`, `format`, `resolve`, `self._activate_opened_vault`, `self._display_active_vault`, `self._status`, `self.exit`, `sessions.close`, `str`.

**Forma del flusso di controllo:** 6 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 4 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** filesystem.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_close_vault -->
#### `main.KeysApp.action_close_vault`

**Tipo:** funzione/metodo  
**Righe:** 1167-1177  
**Firma:** `def action_close_vault(self) -> None`  
**Scopo:** Implementa l'operazione `action_close_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `format`, `self._display_active_vault`, `self._status`, `self.exit`, `sessions.close`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_preferences -->
#### `main.KeysApp.action_preferences`

**Tipo:** funzione/metodo  
**Righe:** 1179-1180  
**Firma:** `def action_preferences(self) -> None`  
**Scopo:** Implementa l'operazione `action_preferences` in questo modulo.

**Chiamate dirette osservate nel corpo:** `PreferencesScreen`, `_`, `self._status`, `self.push_screen`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_help -->
#### `main.KeysApp.action_help`

**Tipo:** funzione/metodo  
**Righe:** 1182-1183  
**Firma:** `def action_help(self) -> None`  
**Scopo:** Implementa l'operazione `action_help` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ChoiceScreen`, `_`, `self.push_screen`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_shortcut_help -->
#### `main.KeysApp.action_shortcut_help`

**Tipo:** funzione/metodo  
**Righe:** 1185-1186  
**Firma:** `def action_shortcut_help(self) -> None`  
**Scopo:** Implementa l'operazione `action_shortcut_help` in questo modulo.

**Chiamate dirette osservate nel corpo:** `HelpScreen`, `self.push_screen`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_help -->
#### `main.KeysApp._finish_help`

**Tipo:** funzione/metodo  
**Righe:** 1188-1190  
**Firma:** `def _finish_help(self, resource) -> None`  
**Scopo:** Helper interno che implementa `_finish_help`.

**Chiamate dirette osservate nel corpo:** `HelpScreen`, `self.push_screen`, `str`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_inbox -->
#### `main.KeysApp.action_inbox`

**Tipo:** funzione/metodo  
**Righe:** 1192-1195  
**Firma:** `def action_inbox(self) -> None`  
**Scopo:** Implementa l'operazione `action_inbox` in questo modulo.

**Chiamate dirette osservate nel corpo:** `InboxScreen`, `_`, `self._status`, `self.action_reload_tree`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_trusted_signers -->
#### `main.KeysApp.action_trusted_signers`

**Tipo:** funzione/metodo  
**Righe:** 1197-1198  
**Firma:** `def action_trusted_signers(self) -> None`  
**Scopo:** Implementa l'operazione `action_trusted_signers` in questo modulo.

**Chiamate dirette osservate nel corpo:** `TrustedSignersScreen`, `self.push_screen`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._copy -->
#### `main.KeysApp._copy`

**Tipo:** funzione/metodo  
**Righe:** 1200-1213  
**Firma:** `def _copy(self, value: str, timeout: int, success: str) -> None`  
**Scopo:** Helper interno che implementa `_copy`.

**Chiamate dirette osservate nel corpo:** `_`, `copy_secret_cli`, `self._show_clipboard_banner`, `self.copy_to_clipboard`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 2 blocchi try, 0 context manager, 2 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** clipboard.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_url -->
#### `main.KeysApp.action_copy_url`

**Tipo:** funzione/metodo  
**Righe:** 1215-1220  
**Firma:** `def action_copy_url(self) -> None`  
**Scopo:** Implementa l'operazione `action_copy_url` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `next`, `self._copy`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_uuid -->
#### `main.KeysApp.action_copy_uuid`

**Tipo:** funzione/metodo  
**Righe:** 1222-1224  
**Firma:** `def action_copy_uuid(self) -> None`  
**Scopo:** Implementa l'operazione `action_copy_uuid` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `self._copy`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_username -->
#### `main.KeysApp.action_copy_username`

**Tipo:** funzione/metodo  
**Righe:** 1226-1233  
**Firma:** `def action_copy_username(self) -> None`  
**Scopo:** Implementa l'operazione `action_copy_username` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `self._copy`, `self._status`, `vault.resolved_username`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_password -->
#### `main.KeysApp.action_copy_password`

**Tipo:** funzione/metodo  
**Righe:** 1235-1242  
**Firma:** `def action_copy_password(self) -> None`  
**Scopo:** Implementa l'operazione `action_copy_password` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `self._copy`, `self._status`, `vault.resolved_password`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_notes -->
#### `main.KeysApp.action_copy_notes`

**Tipo:** funzione/metodo  
**Righe:** 1244-1246  
**Firma:** `def action_copy_notes(self) -> None`  
**Scopo:** Implementa l'operazione `action_copy_notes` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `self._copy`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_copy_totp -->
#### `main.KeysApp.action_copy_totp`

**Tipo:** funzione/metodo  
**Righe:** 1248-1251  
**Firma:** `def action_copy_totp(self) -> None`  
**Scopo:** Implementa l'operazione `action_copy_totp` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `generate_totp`, `self._copy`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_open_action -->
#### `main.KeysApp.action_open_action`

**Tipo:** funzione/metodo  
**Righe:** 1253-1259  
**Firma:** `def action_open_action(self) -> None`  
**Scopo:** Implementa l'operazione `action_open_action` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `launch_action`, `self._status`, `vault.resolved_action`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_new_entry -->
#### `main.KeysApp.action_new_entry`

**Tipo:** funzione/metodo  
**Righe:** 1261-1266  
**Firma:** `def action_new_entry(self) -> None`  
**Scopo:** Implementa l'operazione `action_new_entry` in questo modulo.

**Chiamate dirette osservate nel corpo:** `EntryDraft`, `EntryEditorScreen`, `_`, `self._status`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_new_entry -->
#### `main.KeysApp._finish_new_entry`

**Tipo:** funzione/metodo  
**Righe:** 1268-1276  
**Firma:** `def _finish_new_entry(self, draft: EntryDraft | None) -> None`  
**Scopo:** Helper interno che implementa `_finish_new_entry`.

**Chiamate dirette osservate nel corpo:** `_`, `build_entry_from_draft`, `self._refresh_after_mutation`, `self._status`, `vault.save_entry`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_edit_selected -->
#### `main.KeysApp.action_edit_selected`

**Tipo:** funzione/metodo  
**Righe:** 1278-1290  
**Firma:** `def action_edit_selected(self) -> None`  
**Scopo:** Implementa l'operazione `action_edit_selected` in questo modulo.

**Chiamate dirette osservate nel corpo:** `EntryDraft.from_entry`, `EntryEditorScreen`, `NameScreen`, `_`, `self._finish_edit_entry`, `self._status`, `self.push_screen`, `vault.get_folder`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_edit_entry -->
#### `main.KeysApp._finish_edit_entry`

**Tipo:** funzione/metodo  
**Righe:** 1292-1303  
**Firma:** `def _finish_edit_entry(self, entry_id: str, draft: EntryDraft | None) -> None`  
**Scopo:** Helper interno che implementa `_finish_edit_entry`.

**Chiamate dirette osservate nel corpo:** `_`, `build_entry_from_draft`, `self._refresh_after_mutation`, `self._status`, `vault.get_entry`, `vault.save_entry`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_new_folder -->
#### `main.KeysApp.action_new_folder`

**Tipo:** funzione/metodo  
**Righe:** 1305-1309  
**Firma:** `def action_new_folder(self) -> None`  
**Scopo:** Implementa l'operazione `action_new_folder` in questo modulo.

**Chiamate dirette osservate nel corpo:** `NameScreen`, `_`, `self._status`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_new_folder -->
#### `main.KeysApp._finish_new_folder`

**Tipo:** funzione/metodo  
**Righe:** 1311-1318  
**Firma:** `def _finish_new_folder(self, name: str | None) -> None`  
**Scopo:** Helper interno che implementa `_finish_new_folder`.

**Chiamate dirette osservate nel corpo:** `_`, `self._refresh_after_mutation`, `self._status`, `vault.create_folder`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_rename_folder -->
#### `main.KeysApp._finish_rename_folder`

**Tipo:** funzione/metodo  
**Righe:** 1320-1328  
**Firma:** `def _finish_rename_folder(self, name: str | None) -> None`  
**Scopo:** Helper interno che implementa `_finish_rename_folder`.

**Chiamate dirette osservate nel corpo:** `_`, `self._refresh_after_mutation`, `self._status`, `vault.rename_folder`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_move_selected -->
#### `main.KeysApp.action_move_selected`

**Tipo:** funzione/metodo  
**Righe:** 1330-1335  
**Firma:** `def action_move_selected(self) -> None`  
**Scopo:** Implementa l'operazione `action_move_selected` in questo modulo.

**Chiamate dirette osservate nel corpo:** `MoveScreen`, `_`, `self.push_screen`, `vault.get_folder`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_move -->
#### `main.KeysApp._finish_move`

**Tipo:** funzione/metodo  
**Righe:** 1337-1349  
**Firma:** `def _finish_move(self, destination: str | None | bool) -> None`  
**Scopo:** Helper interno che implementa `_finish_move`.

**Chiamate dirette osservate nel corpo:** `_`, `self._refresh_after_mutation`, `self._status`, `vault.move_entry`, `vault.move_folder`.

**Forma del flusso di controllo:** 2 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_delete_selected -->
#### `main.KeysApp.action_delete_selected`

**Tipo:** funzione/metodo  
**Righe:** 1351-1355  
**Firma:** `def action_delete_selected(self) -> None`  
**Scopo:** Implementa l'operazione `action_delete_selected` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ConfirmScreen`, `_`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_delete -->
#### `main.KeysApp._finish_delete`

**Tipo:** funzione/metodo  
**Righe:** 1357-1371  
**Firma:** `def _finish_delete(self, confirmed: bool) -> None`  
**Scopo:** Helper interno che implementa `_finish_delete`.

**Chiamate dirette osservate nel corpo:** `_`, `self._refresh_after_mutation`, `self._status`, `vault.delete_entry`, `vault.delete_folder`.

**Forma del flusso di controllo:** 3 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 2 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_export_entry -->
#### `main.KeysApp.action_export_entry`

**Tipo:** funzione/metodo  
**Righe:** 1373-1383  
**Firma:** `def action_export_entry(self) -> None`  
**Scopo:** Implementa l'operazione `action_export_entry` in questo modulo.

**Chiamate dirette osservate nel corpo:** `ConfirmScreen`, `_`, `self._finish_export_entry`, `self.push_screen`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp._finish_export_entry -->
#### `main.KeysApp._finish_export_entry`

**Tipo:** funzione/metodo  
**Righe:** 1385-1395  
**Firma:** `def _finish_export_entry(self, confirmed: bool, entry_id: str) -> None`  
**Scopo:** Helper interno che implementa `_finish_export_entry`.

**Chiamate dirette osservate nel corpo:** `Path.cwd`, `_`, `ch.isalnum`, `export_entry_xml`, `format`, `join`, `self._status`, `strip`, `vault.get_entry`, `write_export`.

**Forma del flusso di controllo:** 1 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 1 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_lock_vault -->
#### `main.KeysApp.action_lock_vault`

**Tipo:** funzione/metodo  
**Righe:** 1397-1401  
**Firma:** `def action_lock_vault(self) -> None`  
**Scopo:** Implementa l'operazione `action_lock_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `self._reset_selection`, `self._status`, `self.query_one`, `update`, `vault.lock`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_hard_lock_vault -->
#### `main.KeysApp.action_hard_lock_vault`

**Tipo:** funzione/metodo  
**Righe:** 1403-1408  
**Firma:** `def action_hard_lock_vault(self) -> None`  
**Scopo:** Implementa l'operazione `action_hard_lock_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `self._reset_selection`, `self._status`, `self.query_one`, `sessions.lock_all`, `update`, `vault.crypto.hard_lock`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 0 blocchi try, 0 context manager, 0 return espliciti.

**Categorie di effetti rilevanti per la sicurezza:** cryptography/key-agent.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

<!-- symbol:keys_ng.tui.main:main.KeysApp.action_unlock_vault -->
#### `main.KeysApp.action_unlock_vault`

**Tipo:** funzione/metodo  
**Righe:** 1410-1417  
**Firma:** `def action_unlock_vault(self) -> None`  
**Scopo:** Implementa l'operazione `action_unlock_vault` in questo modulo.

**Chiamate dirette osservate nel corpo:** `_`, `focus`, `self._status`, `self.query_one`, `self.rebuild_tree`, `value.strip`, `vault.unlock`.

**Forma del flusso di controllo:** 0 blocchi condizionali, 0 cicli, 1 blocchi try, 0 context manager, 0 return espliciti.

**Nota per il revisore:** Rivedere le chiamate dirette elencate insieme alle validazioni che le precedono e alla pulizia/gestione errori che le segue; i numeri di riga sopra sono normativi.

## Garanzia di copertura

Questa edizione documenta **535** simboli classe/funzione rilevati tramite attraversamento AST. `tests/test_code_review_manual_coverage.py` attraversa indipendentemente il sorgente della release e richiede un marker per ogni simbolo in entrambe le edizioni linguistiche.

I campi generati, come chiamate dirette e conteggi del flusso di controllo, sono ausili descrittivi di analisi statica; non dimostrano la sicurezza. Il revisore deve ispezionare il sorgente referenziato e il threat model/security review separati.
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

<!-- symbol:keys_ng.services.clipboard:copy_secret_cli.read_acknowledgement -->
<!-- symbol:keys_ng.tui.main:main._select_value_is_blank -->


<!-- symbol:keys_ng.tui.main:main.PreferencesScreen._lines -->
<!-- symbol:keys_ng.tui.main:main.PreferencesScreen._verify_gnupg -->
