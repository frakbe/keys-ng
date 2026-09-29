from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from keys_ng.errors import VaultError

CONFIG_FILE = "vault.json"
_PRIVACY_LEVELS = {"minimal", "standard", "full"}


@dataclass(slots=True)
class VaultConfig:
    recipients: list[str]
    signer: str | None
    trusted_signers: list[str]
    require_signature: bool = True
    catalog_privacy: str = "standard"
    schema: int = 1

    def validate(self) -> None:
        if self.catalog_privacy not in _PRIVACY_LEVELS:
            raise VaultError(f"Unsupported catalog privacy level: {self.catalog_privacy}")
        if not self.recipients:
            raise VaultError("Vault must have at least one recipient")
        if self.require_signature and not self.signer:
            raise VaultError("A signing key is required when signature verification is enabled")
        if self.require_signature and not self.trusted_signers:
            raise VaultError("At least one trusted signer is required when signature verification is enabled")

    def to_json(self) -> str:
        self.validate()
        return json.dumps(
            {
                "schema": self.schema,
                "recipients": self.recipients,
                "signer": self.signer,
                "trusted_signers": self.trusted_signers,
                "require_signature": self.require_signature,
                "catalog_privacy": self.catalog_privacy,
            },
            indent=2,
            sort_keys=True,
        ) + "\n"

    @classmethod
    def load(cls, vault_path: Path) -> "VaultConfig":
        path = vault_path / CONFIG_FILE
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise VaultError(f"Cannot read vault configuration: {exc}") from exc
        if data.get("schema") != 1:
            raise VaultError("Unsupported vault configuration schema")
        data.setdefault("catalog_privacy", "standard")
        config = cls(**data)
        config.validate()
        return config
