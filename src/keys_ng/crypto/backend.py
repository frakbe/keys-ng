from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class DecryptionResult:
    plaintext: bytes
    signer_fingerprint: str | None
    signature_valid: bool
    primary_signer_fingerprint: str | None = None


@dataclass(slots=True, frozen=True)
class KeyInfo:
    fingerprint: str
    user_ids: tuple[str, ...]
    can_encrypt: bool
    can_sign: bool
    secret: bool
    revoked: bool = False
    expired: bool = False

    @property
    def label(self) -> str:
        identity = self.user_ids[0] if self.user_ids else "(no user id)"
        return f"{identity} [{self.fingerprint}]"


class CryptoBackend(ABC):
    @abstractmethod
    def encrypt(self, plaintext: bytes, recipients: list[str], signer: str | None = None) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, ciphertext: bytes) -> DecryptionResult:
        raise NotImplementedError

    @abstractmethod
    def diagnose(self) -> list[tuple[str, bool, str]]:
        raise NotImplementedError

    def list_keys(self, secret: bool = False) -> list[KeyInfo]:
        return []

    def resolve_fingerprint(self, selector: str, secret: bool = False) -> str:
        matches = [k for k in self.list_keys(secret=secret) if k.fingerprint.upper() == selector.upper()]
        if len(matches) == 1:
            return matches[0].fingerprint
        raise ValueError(f"OpenPGP key not found by full fingerprint: {selector}")

    def import_public_key(self, key_data: bytes) -> list[str]:
        """Import public-key material and return available encryption fingerprints.

        Backends that do not support key import may raise ``NotImplementedError``.
        """
        raise NotImplementedError("This crypto backend does not support public-key import")

    def hard_lock(self) -> None:
        """Drop any cached private-key authorization if supported by the backend."""
        return None
