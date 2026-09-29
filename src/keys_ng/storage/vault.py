from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import time
from pathlib import Path
from urllib.parse import urlparse
import os

from keys_ng.crypto.backend import CryptoBackend
from keys_ng.services.diagnostics import elapsed_ms, get_logger
from keys_ng.errors import ReferenceError, SignatureError, VaultError
from keys_ng.models import Action, Catalog, CatalogItem, Entry, Folder, FolderStore, utc_now
from keys_ng.services.references import parse_entry_reference
from keys_ng.storage.atomic import atomic_write_ciphertext, remove_stale_ciphertext_temps
from keys_ng.storage.config import CONFIG_FILE, VaultConfig

CATALOG_FILE = "catalog.gpg"
FOLDERS_FILE = "folders.gpg"
RECORDS_DIR = "records"
INBOX_DIR = "inbox"


_LOG = get_logger("storage.vault")

class Vault:
    def __init__(self, path: str | Path, crypto: CryptoBackend) -> None:
        self.path = Path(path).expanduser().resolve()
        self.crypto = crypto
        self.config = VaultConfig.load(self.path)
        self._locked = False
        # Decrypted metadata caches. The catalog and folder tree are intentionally
        # kept in RAM while the vault is unlocked so interactive search never
        # invokes GnuPG once per item/folder. They are cleared on lock.
        self._catalog_cache: Catalog | None = None
        self._folders_cache: FolderStore | None = None
        self.recover_interrupted_writes()

    @classmethod
    def init(
        cls,
        path: str | Path,
        crypto: CryptoBackend,
        recipients: list[str],
        signer: str | None,
        require_signature: bool = True,
        catalog_privacy: str = "standard",
    ) -> "Vault":
        root = Path(path).expanduser().resolve()
        if root.exists() and any(root.iterdir()):
            raise VaultError("Vault directory is not empty")
        (root / RECORDS_DIR).mkdir(parents=True, exist_ok=True, mode=0o700)
        (root / INBOX_DIR).mkdir(parents=True, exist_ok=True, mode=0o700)
        if os.name != "nt":
            os.chmod(root, 0o700)
            os.chmod(root / RECORDS_DIR, 0o700)
            os.chmod(root / INBOX_DIR, 0o700)
        trusted = [signer] if signer else []
        config = VaultConfig(recipients, signer, trusted, require_signature=require_signature, catalog_privacy=catalog_privacy)
        config_path = root / CONFIG_FILE
        config_path.write_text(config.to_json(), encoding="utf-8")
        if os.name != "nt":
            os.chmod(config_path, 0o600)
        vault = cls(root, crypto)
        vault._write_folders(FolderStore())
        vault._write_catalog(Catalog())
        return vault

    def recover_interrupted_writes(self) -> int:
        removed = remove_stale_ciphertext_temps(self.path)
        removed += remove_stale_ciphertext_temps(self.path / RECORDS_DIR)
        removed += remove_stale_ciphertext_temps(self.path / INBOX_DIR)
        return removed

    @property
    def locked(self) -> bool:
        return self._locked

    def lock(self, hard: bool = False) -> None:
        self._locked = True
        self._catalog_cache = None
        self._folders_cache = None
        if hard:
            self.crypto.hard_lock()

    def unlock(self) -> None:
        self._locked = False
        try:
            self.load_catalog()
            self.load_folders()
        except Exception:
            self._locked = True
            raise

    def _require_unlocked(self) -> None:
        if self._locked:
            raise VaultError("Vault is locked")

    def _verify(self, signer_fingerprint: str | None, signature_valid: bool, primary_signer_fingerprint: str | None = None) -> None:
        if not self.config.require_signature:
            return
        if not signature_valid or not signer_fingerprint:
            raise SignatureError("Encrypted object is not signed with a valid OpenPGP signature")
        normalized = (primary_signer_fingerprint or signer_fingerprint).upper()
        trusted = {fp.upper() for fp in self.config.trusted_signers}
        if normalized not in trusted:
            raise SignatureError(f"Signer is not trusted: {signer_fingerprint}")

    def _encrypt(self, plaintext: bytes) -> bytes:
        self._require_unlocked()
        return self.crypto.encrypt(plaintext, self.config.recipients, self.config.signer)

    def _decrypt(self, ciphertext: bytes) -> bytes:
        self._require_unlocked()
        result = self.crypto.decrypt(ciphertext)
        self._verify(result.signer_fingerprint, result.signature_valid, result.primary_signer_fingerprint)
        return result.plaintext

    def _write_catalog(self, catalog: Catalog) -> None:
        cipher = self._encrypt(catalog.to_bytes())
        atomic_write_ciphertext(self.path / CATALOG_FILE, cipher)
        self._catalog_cache = catalog

    def _write_folders(self, store: FolderStore) -> None:
        cipher = self._encrypt(store.to_bytes())
        atomic_write_ciphertext(self.path / FOLDERS_FILE, cipher)
        self._folders_cache = store

    def load_catalog(self) -> Catalog:
        self._require_unlocked()
        if self._catalog_cache is not None:
            return self._catalog_cache
        path = self.path / CATALOG_FILE
        if not path.exists():
            self._catalog_cache = Catalog()
        else:
            self._catalog_cache = Catalog.from_bytes(self._decrypt(path.read_bytes()))
        return self._catalog_cache

    def load_folders(self) -> FolderStore:
        self._require_unlocked()
        if self._folders_cache is not None:
            return self._folders_cache
        path = self.path / FOLDERS_FILE
        if not path.exists():
            # Backward compatibility with M1.0-M1.3 vaults.
            catalog = self.load_catalog()
            self._folders_cache = FolderStore(folders=list(catalog.folders))
        else:
            self._folders_cache = FolderStore.from_bytes(self._decrypt(path.read_bytes()))
        return self._folders_cache

    def _catalog_item(self, entry: Entry, ciphertext: bytes) -> CatalogItem:
        hosts: list[str] = []
        for action in entry.actions:
            if action.type == "url" and action.url:
                host = urlparse(action.url).hostname
                if host:
                    hosts.append(host)
            elif action.type in {"ssh", "rdp"} and action.host:
                hosts.append(action.host)
        capabilities = []
        if entry.password is not None:
            capabilities.append("password")
        if entry.totp:
            capabilities.append("totp")
        if entry.actions:
            capabilities.append("actions")
            capabilities.extend(f"action:{action.type}" for action in entry.actions)
        privacy = self.config.catalog_privacy
        return CatalogItem(
            id=entry.id,
            title=entry.title,
            kind=entry.kind,
            usernames=entry.usernames if privacy == "full" else [],
            tags=entry.tags if privacy in {"standard", "full"} else [],
            url_hosts=sorted(set(hosts)) if privacy == "full" else [],
            capabilities=capabilities,
            revision=entry.revision,
            ciphertext_sha256=sha256(ciphertext).hexdigest(),
            folder_id=entry.folder_id,
        )

    def _sync_catalog_folders(self, catalog: Catalog | None = None, store: FolderStore | None = None) -> Catalog:
        catalog = catalog or self.load_catalog()
        store = store or self.load_folders()
        catalog.folders = list(store.folders)
        return catalog

    def save_entry(self, entry: Entry) -> Entry:
        self._require_unlocked()
        entry.validate()
        if entry.folder_id is not None and entry.folder_id not in {folder.id for folder in self.load_folders().folders}:
            raise VaultError(f"Folder not found: {entry.folder_id}")
        entry.updated_at = utc_now()
        ciphertext = self._encrypt(entry.to_bytes())
        atomic_write_ciphertext(self.path / RECORDS_DIR / f"{entry.id}.gpg", ciphertext)
        catalog = self.load_catalog()
        item = self._catalog_item(entry, ciphertext)
        catalog.items = [existing for existing in catalog.items if existing.id != entry.id]
        catalog.items.append(item)
        catalog.items.sort(key=lambda x: x.title.casefold())
        self._sync_catalog_folders(catalog)
        self._write_catalog(catalog)
        return entry

    def _verify_record_binding(self, entry_id: str, ciphertext: bytes, entry: Entry) -> None:
        """Bind a decrypted record to its signed catalog snapshot.

        This detects replacement or rollback of a single record while the catalog
        remains current. It intentionally does not claim protection against an
        attacker who rolls back the record and the signed catalog together.
        """
        if entry.id != entry_id:
            raise VaultError(f"Record id mismatch: filename={entry_id}, payload={entry.id}")
        item = next((item for item in self.load_catalog().items if item.id == entry_id), None)
        if item is None:
            raise VaultError(f"Record is not present in signed catalog: {entry_id}; run reindex after review")
        digest = sha256(ciphertext).hexdigest()
        if digest != item.ciphertext_sha256:
            raise VaultError(f"Record/catalog ciphertext hash mismatch: {entry_id}; possible rollback or interrupted write")
        if entry.revision != item.revision:
            raise VaultError(f"Record/catalog revision mismatch: {entry_id}")

    def get_entry(self, entry_id: str) -> Entry:
        self._require_unlocked()
        started = time.perf_counter()
        _LOG.debug("vault.get_entry.start")
        path = self.path / RECORDS_DIR / f"{entry_id}.gpg"
        if not path.exists():
            _LOG.warning("vault.get_entry.missing duration_ms=%.1f", elapsed_ms(started))
            raise VaultError(f"Entry not found: {entry_id}")
        read_started = time.perf_counter()
        ciphertext = path.read_bytes()
        _LOG.debug("vault.get_entry.read_ciphertext duration_ms=%.1f bytes=%d", elapsed_ms(read_started), len(ciphertext))
        decrypt_started = time.perf_counter()
        plaintext = self._decrypt(ciphertext)
        _LOG.debug("vault.get_entry.decrypt duration_ms=%.1f plaintext_bytes=%d", elapsed_ms(decrypt_started), len(plaintext))
        parse_started = time.perf_counter()
        entry = Entry.from_bytes(plaintext)
        _LOG.debug("vault.get_entry.parse duration_ms=%.1f", elapsed_ms(parse_started))
        verify_started = time.perf_counter()
        self._verify_record_binding(entry_id, ciphertext, entry)
        _LOG.debug("vault.get_entry.verify_binding duration_ms=%.1f", elapsed_ms(verify_started))
        _LOG.info("vault.get_entry.end duration_ms=%.1f", elapsed_ms(started))
        return entry

    def resolve_reference_value(
        self,
        value: str | None,
        *,
        _stack: tuple[tuple[str, str], ...] = (),
        _max_depth: int = 32,
    ) -> str | None:
        """Resolve a KeePassXC-style UUID reference stored as a whole field.

        Keys NG intentionally implements the UUID subset requested for reusable
        credentials: {REF:U@I:<UUID>} and {REF:P@I:<UUID>}. References can be
        chained, but cycles and excessive nesting are rejected.
        """
        ref = parse_entry_reference(value)
        if ref is None:
            return value
        key = (ref.entry_id, ref.field)
        if key in _stack:
            chain = " -> ".join(f"{entry_id}:{field}" for entry_id, field in (*_stack, key))
            raise ReferenceError(f"Entry reference cycle detected: {chain}")
        if len(_stack) >= _max_depth:
            raise ReferenceError("Entry reference nesting is too deep")
        try:
            target = self.get_entry(ref.entry_id)
        except VaultError as exc:
            raise ReferenceError(f"Referenced entry not found: {ref.entry_id}") from exc
        raw: str | None
        if ref.field == "U":
            raw = target.usernames[0] if target.usernames else None
        else:
            raw = target.password
        if raw is None:
            raise ReferenceError(f"Referenced {ref.field_name} is empty: {ref.entry_id}")
        return self.resolve_reference_value(raw, _stack=(*_stack, key), _max_depth=_max_depth)

    def resolved_username(self, entry: Entry | str) -> str | None:
        obj = self.get_entry(entry) if isinstance(entry, str) else entry
        raw = obj.usernames[0] if obj.usernames else None
        return self.resolve_reference_value(raw)

    def resolved_password(self, entry: Entry | str) -> str | None:
        obj = self.get_entry(entry) if isinstance(entry, str) else entry
        return self.resolve_reference_value(obj.password)

    def resolved_action(self, entry: Entry, action: Action) -> Action:
        """Return an action with any UUID-referenced username resolved."""
        username = action.username
        if username is None and action.type in {"ssh", "rdp"}:
            username = entry.usernames[0] if entry.usernames else None
        resolved = self.resolve_reference_value(username)
        return replace(action, username=resolved)

    def delete_entry(self, entry_id: str) -> None:
        self._require_unlocked()
        path = self.path / RECORDS_DIR / f"{entry_id}.gpg"
        try:
            path.unlink()
        except FileNotFoundError as exc:
            raise VaultError(f"Entry not found: {entry_id}") from exc
        catalog = self.load_catalog()
        catalog.items = [item for item in catalog.items if item.id != entry_id]
        self._write_catalog(catalog)

    def list_items(self, folder_id: str | None = None, recursive: bool = False) -> list[CatalogItem]:
        items = self.load_catalog().items
        if folder_id is None:
            return items
        allowed = {folder_id}
        if recursive:
            folders = self.load_folders().folders
            changed = True
            while changed:
                changed = False
                for folder in folders:
                    if folder.parent_id in allowed and folder.id not in allowed:
                        allowed.add(folder.id)
                        changed = True
        return [item for item in items if item.folder_id in allowed]

    @staticmethod
    def _folder_paths_from(folders: list[Folder]) -> dict[str, str]:
        """Build all folder paths in O(n) without repeated vault decryptions."""
        by_id = {folder.id: folder for folder in folders}
        cache: dict[str, str] = {}

        def resolve(folder_id: str, visiting: set[str] | None = None) -> str:
            if folder_id in cache:
                return cache[folder_id]
            visiting = set() if visiting is None else visiting
            if folder_id in visiting:
                raise VaultError("Folder hierarchy cycle")
            folder = by_id.get(folder_id)
            if folder is None:
                raise VaultError(f"Folder not found: {folder_id}")
            visiting.add(folder_id)
            if folder.parent_id:
                parent = resolve(folder.parent_id, visiting)
                path = f"{parent}/{folder.name}" if parent else folder.name
            else:
                path = folder.name
            visiting.remove(folder_id)
            cache[folder_id] = path
            return path

        for folder_id in by_id:
            resolve(folder_id)
        return cache

    def folder_paths(self, *, catalog_snapshot: bool = False) -> dict[str, str]:
        folders = self.load_catalog().folders if catalog_snapshot else self.load_folders().folders
        return self._folder_paths_from(folders)

    def search(self, query: str) -> list[CatalogItem]:
        needle = query.casefold().strip()
        catalog = self.load_catalog()
        if not needle:
            return list(catalog.items)
        # The catalog contains a signed/encrypted snapshot of the folder tree.
        # Using it here means a CLI search normally requires one GPG decrypt total.
        folder_names = self._folder_paths_from(catalog.folders) if catalog.folders else {}
        matches = []
        for item in catalog.items:
            haystack = " ".join(
                [item.title, item.kind, *item.usernames, *item.tags, *item.url_hosts, *item.capabilities, folder_names.get(item.folder_id, "")]
            ).casefold()
            if needle in haystack:
                matches.append(item)
        return matches

    def reindex(self) -> Catalog:
        self._require_unlocked()
        items: list[CatalogItem] = []
        for path in sorted((self.path / RECORDS_DIR).glob("*.gpg")):
            ciphertext = path.read_bytes()
            entry = Entry.from_bytes(self._decrypt(ciphertext))
            items.append(self._catalog_item(entry, ciphertext))
        store = self.load_folders()
        catalog = Catalog(items=sorted(items, key=lambda x: x.title.casefold()), folders=list(store.folders))
        self._write_catalog(catalog)
        return catalog

    def catalog_health(self) -> tuple[bool, list[str]]:
        catalog = self.load_catalog()
        issues: list[str] = []
        by_id = {item.id: item for item in catalog.items}
        record_ids = {path.stem for path in (self.path / RECORDS_DIR).glob("*.gpg")}
        folder_ids = {folder.id for folder in self.load_folders().folders}
        for entry_id in sorted(record_ids):
            path = self.path / RECORDS_DIR / f"{entry_id}.gpg"
            item = by_id.get(entry_id)
            if item is None:
                issues.append(f"record missing from catalog: {entry_id}")
                continue
            digest = sha256(path.read_bytes()).hexdigest()
            if digest != item.ciphertext_sha256:
                issues.append(f"catalog hash mismatch: {entry_id}")
            if item.folder_id is not None and item.folder_id not in folder_ids:
                issues.append(f"entry references missing folder: {entry_id}")
        for entry_id in sorted(set(by_id) - record_ids):
            issues.append(f"catalog references missing record: {entry_id}")
        if {f.id for f in catalog.folders} != folder_ids:
            issues.append("catalog folder snapshot differs from folders.gpg")
        return not issues, issues

    # Folder API ---------------------------------------------------------
    def list_folders(self) -> list[Folder]:
        folders = list(self.load_folders().folders)
        paths = self._folder_paths_from(folders)
        return sorted(folders, key=lambda folder: paths[folder.id].casefold())

    def get_folder(self, folder_id: str) -> Folder:
        for folder in self.load_folders().folders:
            if folder.id == folder_id:
                return folder
        raise VaultError(f"Folder not found: {folder_id}")

    def folder_path(self, folder_id: str | None) -> str:
        if folder_id is None:
            return ""
        paths = self.folder_paths()
        if folder_id not in paths:
            raise VaultError(f"Folder not found: {folder_id}")
        return paths[folder_id]

    def resolve_folder_path(self, path: str) -> str | None:
        path = path.strip().strip("/\\")
        if not path:
            return None
        folders = self.load_folders().folders
        parent_id: str | None = None
        for part in [part for part in path.replace("\\", "/").split("/") if part]:
            matches = [folder for folder in folders if folder.parent_id == parent_id and folder.name.casefold() == part.casefold()]
            if not matches:
                raise VaultError(f"Folder path not found: {path}")
            if len(matches) > 1:
                raise VaultError(f"Ambiguous folder path: {path}")
            parent_id = matches[0].id
        return parent_id

    def create_folder(self, name: str, parent_id: str | None = None) -> Folder:
        self._require_unlocked()
        store = self.load_folders()
        if parent_id is not None and parent_id not in {folder.id for folder in store.folders}:
            raise VaultError(f"Parent folder not found: {parent_id}")
        if any(folder.parent_id == parent_id and folder.name.casefold() == name.strip().casefold() for folder in store.folders):
            raise VaultError("A folder with that name already exists here")
        folder = Folder.create(name.strip(), parent_id)
        folder.validate()
        store.folders.append(folder)
        store.validate()
        self._write_folders(store)
        catalog = self.load_catalog()
        self._sync_catalog_folders(catalog, store)
        self._write_catalog(catalog)
        return folder

    def create_folder_path(self, path: str) -> Folder | None:
        normalized = path.strip().strip("/\\")
        if not normalized:
            return None
        parent_id: str | None = None
        last: Folder | None = None
        for part in [part for part in normalized.replace("\\", "/").split("/") if part]:
            store = self.load_folders()
            existing = next((folder for folder in store.folders if folder.parent_id == parent_id and folder.name.casefold() == part.casefold()), None)
            if existing:
                last = existing
            else:
                last = self.create_folder(part, parent_id)
            parent_id = last.id
        return last

    def rename_folder(self, folder_id: str, new_name: str) -> Folder:
        current = self.load_folders()
        store = FolderStore(folders=[replace(folder) for folder in current.folders], schema=current.schema)
        folder = next((folder for folder in store.folders if folder.id == folder_id), None)
        if folder is None:
            raise VaultError(f"Folder not found: {folder_id}")
        normalized = new_name.strip()
        if any(other.id != folder.id and other.parent_id == folder.parent_id and other.name.casefold() == normalized.casefold() for other in store.folders):
            raise VaultError("A folder with that name already exists here")
        folder.name = normalized
        folder.updated_at = utc_now()
        store.validate()
        self._write_folders(store)
        catalog = self.load_catalog()
        self._sync_catalog_folders(catalog, store)
        self._write_catalog(catalog)
        return folder

    def move_folder(self, folder_id: str, parent_id: str | None) -> Folder:
        current = self.load_folders()
        store = FolderStore(folders=[replace(folder) for folder in current.folders], schema=current.schema)
        by_id = {folder.id: folder for folder in store.folders}
        folder = by_id.get(folder_id)
        if folder is None:
            raise VaultError(f"Folder not found: {folder_id}")
        if parent_id is not None and parent_id not in by_id:
            raise VaultError(f"Parent folder not found: {parent_id}")
        if parent_id == folder_id:
            raise VaultError("Folder cannot be its own parent")
        if any(other.id != folder.id and other.parent_id == parent_id and other.name.casefold() == folder.name.casefold() for other in store.folders):
            raise VaultError("A folder with that name already exists here")
        folder.parent_id = parent_id
        folder.updated_at = utc_now()
        # FolderStore.validate detects attempts to move a folder below one of
        # its descendants. Because this method edits a clone, a rejected move
        # cannot poison the decrypted in-memory folder cache.
        store.validate()
        self._write_folders(store)
        catalog = self.load_catalog()
        self._sync_catalog_folders(catalog, store)
        self._write_catalog(catalog)
        return folder

    def delete_folder(self, folder_id: str) -> None:
        store = self.load_folders()
        if any(folder.parent_id == folder_id for folder in store.folders):
            raise VaultError("Folder contains subfolders")
        if any(item.folder_id == folder_id for item in self.load_catalog().items):
            raise VaultError("Folder contains entries")
        before = len(store.folders)
        store.folders = [folder for folder in store.folders if folder.id != folder_id]
        if len(store.folders) == before:
            raise VaultError(f"Folder not found: {folder_id}")
        self._write_folders(store)
        catalog = self.load_catalog()
        self._sync_catalog_folders(catalog, store)
        self._write_catalog(catalog)

    def move_entry(self, entry_id: str, folder_id: str | None) -> Entry:
        if folder_id is not None and folder_id not in {folder.id for folder in self.load_folders().folders}:
            raise VaultError(f"Folder not found: {folder_id}")
        entry = self.get_entry(entry_id)
        entry.folder_id = folder_id
        entry.revision += 1
        return self.save_entry(entry)
