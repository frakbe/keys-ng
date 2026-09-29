from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from keys_ng.crypto.backend import CryptoBackend, KeyInfo
from keys_ng.errors import VaultError
from keys_ng.storage.vault import Vault


@dataclass(slots=True, frozen=True)
class VaultInitRequest:
    path: str | Path
    recipients: tuple[str, ...]
    signer: str | None
    require_signature: bool = True
    catalog_privacy: str = "standard"


@dataclass(slots=True, frozen=True)
class VaultInitChoices:
    recipients: tuple[KeyInfo, ...]
    signers: tuple[KeyInfo, ...]


def available_vault_keys(crypto: CryptoBackend) -> VaultInitChoices:
    """Return usable public encryption keys and secret signing keys."""
    recipients = tuple(
        key for key in crypto.list_keys(secret=False)
        if key.can_encrypt and not key.revoked and not key.expired
    )
    signers = tuple(
        key for key in crypto.list_keys(secret=True)
        if key.can_sign and not key.revoked and not key.expired
    )
    return VaultInitChoices(recipients, signers)


def validate_vault_target(path: str | Path) -> Path:
    """Validate the target without creating or deleting user data."""
    root = Path(path).expanduser().resolve()
    if root.exists():
        if not root.is_dir():
            raise VaultError("Vault path exists and is not a directory")
        try:
            if any(root.iterdir()):
                raise VaultError("Vault directory is not empty")
        except OSError as exc:
            raise VaultError(f"Unable to inspect vault directory: {exc}") from exc
    else:
        parent = root.parent
        if not parent.exists() or not parent.is_dir():
            raise VaultError("Parent directory does not exist")
    return root


def _normalize_request(request: VaultInitRequest, crypto: CryptoBackend) -> VaultInitRequest:
    if request.catalog_privacy not in {"minimal", "standard", "full"}:
        raise VaultError("Invalid catalog privacy mode")
    if not request.recipients:
        raise VaultError("At least one recipient is required")
    recipients = tuple(crypto.resolve_fingerprint(fp, secret=False) for fp in request.recipients)
    signer = crypto.resolve_fingerprint(request.signer, secret=True) if request.signer else None
    if request.require_signature and not signer:
        raise VaultError("A signing key is required when signature verification is enabled")
    return VaultInitRequest(
        path=validate_vault_target(request.path),
        recipients=recipients,
        signer=signer,
        require_signature=request.require_signature,
        catalog_privacy=request.catalog_privacy,
    )


def run_vault_crypto_self_test(crypto: CryptoBackend, recipients: tuple[str, ...], signer: str | None, require_signature: bool) -> None:
    """Verify encrypt/decrypt/signature behavior before writing a new vault."""
    probe = b"keys-ng vault creation self-test v1"
    ciphertext = crypto.encrypt(probe, list(recipients), signer)
    result = crypto.decrypt(ciphertext)
    if result.plaintext != probe:
        raise VaultError("GnuPG self-test failed: decrypted plaintext mismatch")
    if require_signature:
        if not result.signature_valid or not result.signer_fingerprint:
            raise VaultError("GnuPG self-test failed: signature was not verified")
        if signer and result.signer_fingerprint.upper() != signer.upper():
            raise VaultError("GnuPG self-test failed: unexpected signing key")


def create_vault(request: VaultInitRequest, crypto: CryptoBackend, *, self_test: bool = True) -> Vault:
    """Create a vault through the shared CLI/GUI/TUI initialization policy."""
    normalized = _normalize_request(request, crypto)
    if self_test:
        run_vault_crypto_self_test(
            crypto,
            normalized.recipients,
            normalized.signer,
            normalized.require_signature,
        )
    return Vault.init(
        normalized.path,
        crypto,
        list(normalized.recipients),
        normalized.signer,
        normalized.require_signature,
        normalized.catalog_privacy,
    )
