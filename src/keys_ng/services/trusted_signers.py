from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from keys_ng.crypto.backend import KeyInfo
from keys_ng.errors import VaultError
from keys_ng.storage.config import CONFIG_FILE
from keys_ng.storage.vault import Vault


@dataclass(slots=True, frozen=True)
class TrustedSignerInfo:
    fingerprint: str
    label: str
    present: bool
    revoked: bool
    expired: bool
    can_sign: bool
    vault_signer: bool


def _save_config(vault: Vault) -> None:
    path = vault.path / CONFIG_FILE
    path.write_text(vault.config.to_json(), encoding="utf-8")
    if os.name != "nt":
        os.chmod(path, 0o600)


def _key_by_fingerprint(vault: Vault, fingerprint: str) -> KeyInfo | None:
    needle = fingerprint.strip().upper()
    return next((key for key in vault.crypto.list_keys(secret=False) if key.fingerprint.upper() == needle), None)


def list_trusted_signers(vault: Vault) -> list[TrustedSignerInfo]:
    keys = {key.fingerprint.upper(): key for key in vault.crypto.list_keys(secret=False)}
    primary = (vault.config.signer or "").upper()
    result: list[TrustedSignerInfo] = []
    for fingerprint in vault.config.trusted_signers:
        fp = fingerprint.upper()
        key = keys.get(fp)
        result.append(
            TrustedSignerInfo(
                fingerprint=fp,
                label=key.label if key else f"(key not present) [{fp}]",
                present=key is not None,
                revoked=bool(key.revoked) if key else False,
                expired=bool(key.expired) if key else False,
                can_sign=bool(key.can_sign) if key else False,
                vault_signer=fp == primary,
            )
        )
    return result


def eligible_signing_keys(vault: Vault) -> list[KeyInfo]:
    return [key for key in vault.crypto.list_keys(secret=False) if key.can_sign and not key.revoked and not key.expired]


def add_trusted_signer(vault: Vault, fingerprint: str) -> TrustedSignerInfo:
    fp = vault.crypto.resolve_fingerprint(fingerprint, secret=False).upper()
    key = _key_by_fingerprint(vault, fp)
    if key is None:
        raise VaultError(f"OpenPGP public key is not available: {fp}")
    if key.revoked:
        raise VaultError(f"OpenPGP key is revoked: {fp}")
    if key.expired:
        raise VaultError(f"OpenPGP key is expired: {fp}")
    if not key.can_sign:
        raise VaultError(f"OpenPGP key is not signing-capable: {fp}")
    current = {value.upper() for value in vault.config.trusted_signers}
    if fp not in current:
        vault.config.trusted_signers.append(fp)
        _save_config(vault)
    return TrustedSignerInfo(fp, key.label, True, key.revoked, key.expired, key.can_sign, fp == (vault.config.signer or "").upper())


def remove_trusted_signer(vault: Vault, fingerprint: str) -> None:
    fp = fingerprint.strip().upper()
    if fp == (vault.config.signer or "").upper():
        raise VaultError("The vault signing key cannot be removed from trusted signers")
    updated = [value for value in vault.config.trusted_signers if value.upper() != fp]
    if len(updated) == len(vault.config.trusted_signers):
        raise VaultError(f"Trusted signer not found: {fingerprint}")
    vault.config.trusted_signers = updated
    _save_config(vault)
