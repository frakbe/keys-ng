from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path
import uuid

from keys_ng.crypto.backend import CryptoBackend, KeyInfo
from keys_ng.models import Entry, utc_now
from keys_ng.storage.inbox import write_encrypted_entry
from keys_ng.storage.vault import Vault


def standalone_recipient_keys(crypto: CryptoBackend) -> list[KeyInfo]:
    """Return usable public encryption keys from the current GnuPG keyring."""
    return [
        key for key in crypto.list_keys(secret=False)
        if key.can_encrypt and not key.revoked and not key.expired
    ]


def standalone_signing_keys(crypto: CryptoBackend) -> list[KeyInfo]:
    """Return usable secret signing keys from the current GnuPG keyring."""
    return [
        key for key in crypto.list_keys(secret=True)
        if key.can_sign and not key.revoked and not key.expired
    ]


def import_standalone_public_key(crypto: CryptoBackend, path: str | Path) -> list[KeyInfo]:
    """Import a public-key file into the active GnuPG keyring and list usable keys."""
    source = Path(path).expanduser()
    if not source.is_file():
        raise ValueError(f"Public-key file not found: {source}")
    imported = crypto.import_public_key(source.read_bytes())
    by_fingerprint = {key.fingerprint.upper(): key for key in standalone_recipient_keys(crypto)}
    result = [by_fingerprint[fingerprint.upper()] for fingerprint in imported if fingerprint.upper() in by_fingerprint]
    if not result:
        raise ValueError("The public-key file contains no usable encryption key")
    return result


def prepare_standalone_entry(vault: Vault, entry: Entry) -> Entry:
    """Create an independent export copy, resolving local UUID references."""
    exported = deepcopy(entry)
    username = vault.resolved_username(entry)
    exported.usernames = [username] if username is not None else []
    exported.password = vault.resolved_password(entry)
    exported.actions = [
        vault.resolved_action(entry, action)
        if action.type in {"ssh", "rdp"}
        else deepcopy(action)
        for action in entry.actions
    ]
    exported.id = str(uuid.uuid4())
    exported.folder_id = None
    exported.revision = 1
    now = utc_now()
    exported.created_at = now
    exported.updated_at = now
    exported.validate()
    return exported


def export_standalone_entry(
    vault: Vault,
    entry_id: str,
    output_path: str | Path,
    recipient: str,
    signer: str | None = None,
) -> tuple[Path, Entry]:
    """Encrypt and optionally sign one vault entry as a standalone record."""
    source = vault.get_entry(entry_id)
    exported = prepare_standalone_entry(vault, source)
    destination = write_encrypted_entry(output_path, exported, vault.crypto, [recipient], signer)
    return destination, exported
