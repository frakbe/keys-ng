from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import time
import uuid

from keys_ng.crypto.backend import CryptoBackend
from keys_ng.models import Entry
from keys_ng.services.diagnostics import elapsed_ms, get_logger
from keys_ng.storage.atomic import atomic_write_ciphertext
from keys_ng.storage.vault import INBOX_DIR, Vault

_LOG = get_logger("storage.inbox")


@dataclass(slots=True)
class InboxInspection:
    path: Path
    entry: Entry | None
    decryptable: bool
    signed: bool
    signature_valid: bool
    signer_fingerprint: str | None
    signer_authorized: bool
    error: str | None = None

    @property
    def importable(self) -> bool:
        return self.decryptable and self.entry is not None and self.signature_valid and self.signer_authorized

    @property
    def status(self) -> str:
        if not self.decryptable:
            return "cannot-decrypt"
        if self.error:
            return "malformed"
        if not self.signed:
            return "unsigned"
        if not self.signature_valid:
            return "invalid-signature"
        if not self.signer_authorized:
            return "untrusted-signer"
        return "trusted"


def write_encrypted_entry(output_path: str | Path, entry: Entry, crypto: CryptoBackend, recipients: list[str], signer: str | None = None) -> Path:
    """Encrypt one standalone entry to an arbitrary ciphertext path."""
    entry.validate()
    destination = Path(output_path).expanduser().resolve()
    ciphertext = crypto.encrypt(entry.to_bytes(), recipients, signer)
    atomic_write_ciphertext(destination, ciphertext)
    return destination


def deposit_entry(vault_path: str | Path, entry: Entry, crypto: CryptoBackend, recipients: list[str], signer: str | None = None) -> Path:
    """Write a new encrypted inbox item without requiring access to the vault catalog."""
    root = Path(vault_path).expanduser().resolve()
    return write_encrypted_entry(root / INBOX_DIR / f"{uuid.uuid4()}.gpg", entry, crypto, recipients, signer)


def pending_inbox_paths(vault: Vault) -> list[Path]:
    """Return pending ciphertexts without decrypting them."""
    return sorted((vault.path / INBOX_DIR).glob("*.gpg"))


def inspect_inbox_item(vault: Vault, path: Path) -> InboxInspection:
    """Decrypt and classify one inbox item without modifying the vault."""
    started = time.perf_counter()
    _LOG.debug("inbox.inspect.start")
    try:
        result = vault.crypto.decrypt(path.read_bytes())
    except Exception as exc:
        _LOG.info("inbox.inspect.end status=cannot-decrypt duration_ms=%.1f", elapsed_ms(started))
        return InboxInspection(path, None, False, False, False, None, False, type(exc).__name__)
    signed = bool(result.signer_fingerprint)
    signer = (result.primary_signer_fingerprint or result.signer_fingerprint)
    authorized = bool(signer and signer.upper() in {fp.upper() for fp in vault.config.trusted_signers})
    try:
        entry = Entry.from_bytes(result.plaintext)
    except Exception as exc:
        _LOG.info("inbox.inspect.end status=malformed duration_ms=%.1f", elapsed_ms(started))
        return InboxInspection(path, None, True, signed, result.signature_valid, signer, authorized, type(exc).__name__)
    inspection = InboxInspection(path, entry, True, signed, result.signature_valid, signer, authorized)
    _LOG.info(
        "inbox.inspect.end status=%s signed=%s signature_valid=%s signer_authorized=%s duration_ms=%.1f",
        inspection.status, signed, result.signature_valid, authorized, elapsed_ms(started),
    )
    return inspection


def inspect_inbox(vault: Vault) -> list[InboxInspection]:
    paths = pending_inbox_paths(vault)
    _LOG.info("inbox.scan count=%d", len(paths))
    return [inspect_inbox_item(vault, path) for path in paths]


def import_inbox_item(vault: Vault, inspection: InboxInspection, *, delete_after: bool = True, accept_unsigned: bool = False) -> str:
    """Import one already inspected item and re-encrypt/sign it with vault policy."""
    started = time.perf_counter()
    _LOG.debug("inbox.import.start status=%s", inspection.status)
    if not inspection.decryptable or inspection.entry is None:
        raise ValueError("inbox item cannot be decrypted or parsed")
    if inspection.signed:
        if not inspection.signature_valid:
            raise ValueError("inbox item has an invalid signature")
        if not inspection.signer_authorized:
            raise ValueError("inbox signature is valid, but the signer is not authorized by this vault")
    elif not accept_unsigned:
        raise ValueError("unsigned inbox item; explicit unsigned approval is required")
    target = vault.path / "records" / f"{inspection.entry.id}.gpg"
    if target.exists():
        raise ValueError(f"entry id already exists: {inspection.entry.id}")
    vault.save_entry(inspection.entry)
    if delete_after:
        inspection.path.unlink()
    _LOG.info("inbox.import.end duration_ms=%.1f", elapsed_ms(started))
    return inspection.entry.id


def delete_inbox_item(vault: Vault, path: Path) -> None:
    resolved = path.resolve()
    inbox = (vault.path / INBOX_DIR).resolve()
    if resolved.parent != inbox or resolved.suffix.lower() != ".gpg":
        raise ValueError("refusing to delete a path outside the vault inbox")
    resolved.unlink()


def import_inbox(vault: Vault, *, delete_after: bool = True, accept_unsigned: bool = False) -> list[tuple[Path, str]]:
    """Import all inbox records, preserving failed source files."""
    results: list[tuple[Path, str]] = []
    for inspection in inspect_inbox(vault):
        try:
            import_inbox_item(vault, inspection, delete_after=delete_after, accept_unsigned=accept_unsigned)
            results.append((inspection.path, "ok"))
        except Exception as exc:
            results.append((inspection.path, f"error: {exc}"))
    return results
