from __future__ import annotations

from keys_ng.crypto.backend import CryptoBackend
from keys_ng.crypto.gpg_process import GPGProcessBackend


def create_crypto_backend(
    preference: str = "auto",
    gpg_executable: str = "",
    gpgconf_executable: str = "",
) -> CryptoBackend:
    """Return the requested backend.

    Explicit GnuPG executable overrides select the subprocess backend so the
    configured paths are honored consistently on every platform.
    """
    normalized = preference.lower()
    if normalized not in {"auto", "gpg", "gpgme"}:
        raise ValueError(f"Unknown crypto backend: {preference}")
    if gpg_executable.strip() or gpgconf_executable.strip():
        if normalized == "gpgme":
            raise ValueError("Explicit GnuPG executable paths require the 'gpg' or 'auto' backend")
        return GPGProcessBackend(gpg_executable or None, gpgconf_executable or None)
    if normalized == "gpgme":
        try:
            from keys_ng.crypto.gpgme_backend import GPGMEBackend
            return GPGMEBackend()
        except (ImportError, RuntimeError) as exc:
            raise RuntimeError(f"GPGME backend is unavailable: {exc}") from exc
    if normalized == "auto":
        try:
            from keys_ng.crypto.gpgme_backend import GPGMEBackend
            return GPGMEBackend()
        except (ImportError, RuntimeError):
            pass
    return GPGProcessBackend()
