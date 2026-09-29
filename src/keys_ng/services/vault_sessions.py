from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from keys_ng.storage.vault import Vault


class VaultSessionManager:
    """Track multiple open vault objects and one active vault.

    The manager deliberately keeps each ``Vault`` instance alive while it is
    open so its lock state and in-memory caches remain independent when the TUI
    switches between vaults.
    """

    def __init__(self, initial: Vault) -> None:
        self._vaults: dict[str, Vault] = {}
        self._active_path = ""
        self.add(initial, activate=True)

    @staticmethod
    def _key(path: str | Path) -> str:
        return str(Path(path).expanduser().resolve())

    @property
    def active(self) -> Vault:
        return self._vaults[self._active_path]

    @property
    def active_path(self) -> str:
        return self._active_path

    def add(self, vault: Vault, *, activate: bool = True) -> Vault:
        key = self._key(vault.path)
        existing = self._vaults.get(key)
        if existing is None:
            self._vaults[key] = vault
            existing = vault
        if activate:
            self._active_path = key
        return existing

    def activate(self, path: str | Path) -> Vault:
        key = self._key(path)
        if key not in self._vaults:
            raise KeyError(key)
        self._active_path = key
        return self._vaults[key]

    def contains(self, path: str | Path) -> bool:
        return self._key(path) in self._vaults

    def opened(self) -> tuple[Vault, ...]:
        return tuple(self._vaults.values())

    def paths(self) -> tuple[str, ...]:
        return tuple(self._vaults)

    def close(self, path: str | Path | None = None) -> Vault | None:
        key = self._key(path) if path is not None else self._active_path
        vault = self._vaults.pop(key)
        try:
            vault.lock(False)
        except Exception:
            pass
        if not self._vaults:
            self._active_path = ""
            return None
        if key == self._active_path:
            self._active_path = next(reversed(self._vaults))
        return self.active

    def lock_all(self) -> None:
        for vault in self._vaults.values():
            vault.lock(False)

    def __len__(self) -> int:
        return len(self._vaults)

    def __iter__(self) -> Iterable[Vault]:
        return iter(self._vaults.values())
