class KeysNGError(Exception):
    """Base application error."""


class CryptoError(KeysNGError):
    """OpenPGP operation failed."""


class SignatureError(CryptoError):
    """A required signature was missing or invalid."""


class VaultError(KeysNGError):
    """Vault storage or configuration error."""


class LegacyFormatError(KeysNGError):
    """Legacy record did not match the strict supported grammar."""


class ReferenceError(KeysNGError):
    """An entry cross-reference was invalid, broken, or cyclic."""
