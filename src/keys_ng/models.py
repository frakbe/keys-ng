from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
import json
import uuid

SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(slots=True)
class TotpConfig:
    secret: str
    issuer: str = ""
    account_name: str = ""
    algorithm: str = "SHA1"
    digits: int = 6
    period: int = 30

    def validate(self) -> None:
        if self.algorithm.upper() not in {"SHA1", "SHA256", "SHA512"}:
            raise ValueError("Unsupported TOTP algorithm")
        if self.digits not in {6, 7, 8}:
            raise ValueError("TOTP digits must be 6, 7, or 8")
        if self.period < 5 or self.period > 300:
            raise ValueError("TOTP period out of allowed range")
        if not self.secret.strip():
            raise ValueError("TOTP secret is empty")


@dataclass(slots=True)
class Action:
    type: str
    url: str | None = None
    host: str | None = None
    port: int | None = None
    username: str | None = None
    argv: list[str] = field(default_factory=list)
    shell: bool = False
    ssh_x11_forwarding: str = "off"
    ssh_options: list[str] = field(default_factory=list)

    def validate(self) -> None:
        if self.shell:
            raise ValueError("Shell actions are not permitted by the default schema")
        if self.type == "url" and not self.url:
            raise ValueError("URL action requires url")
        if self.type in {"ssh", "rdp"} and not self.host:
            raise ValueError(f"{self.type.upper()} action requires host")
        if self.type == "command" and not self.argv:
            raise ValueError("Command action requires argv")
        if self.type not in {"url", "ssh", "rdp", "command"}:
            raise ValueError(f"Unsupported action type: {self.type}")
        if self.ssh_x11_forwarding not in {"off", "X", "Y"}:
            raise ValueError("SSH X11 forwarding must be off, X, or Y")
        if self.type != "ssh" and (self.ssh_x11_forwarding != "off" or self.ssh_options):
            raise ValueError("SSH-specific options are only valid for SSH actions")
        if not all(isinstance(item, str) and item for item in self.ssh_options):
            raise ValueError("SSH advanced options must be non-empty strings")
        if self.type == "ssh":
            from keys_ng.services.ssh_options import validate_ssh_options
            validate_ssh_options(self.ssh_options)
        if self.port is not None and not (1 <= self.port <= 65535):
            raise ValueError("Action port out of range")


@dataclass(slots=True)
class Folder:
    id: str
    name: str
    parent_id: str | None = None
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)

    @classmethod
    def create(cls, name: str, parent_id: str | None = None) -> "Folder":
        return cls(id=str(uuid.uuid4()), name=name, parent_id=parent_id)

    def validate(self) -> None:
        uuid.UUID(self.id)
        if self.parent_id is not None:
            uuid.UUID(self.parent_id)
            if self.parent_id == self.id:
                raise ValueError("Folder cannot be its own parent")
        if not self.name.strip():
            raise ValueError("Folder name is empty")
        if "/" in self.name or "\\" in self.name:
            raise ValueError("Folder name cannot contain path separators")


@dataclass(slots=True)
class FolderStore:
    folders: list[Folder] = field(default_factory=list)
    schema: int = SCHEMA_VERSION

    def validate(self) -> None:
        if self.schema != SCHEMA_VERSION:
            raise ValueError("Unsupported folder-store schema")
        by_id = {folder.id: folder for folder in self.folders}
        if len(by_id) != len(self.folders):
            raise ValueError("Duplicate folder id")
        for folder in self.folders:
            folder.validate()
            if folder.parent_id is not None and folder.parent_id not in by_id:
                raise ValueError(f"Folder parent does not exist: {folder.parent_id}")
        for folder in self.folders:
            seen: set[str] = set()
            current: Folder | None = folder
            while current is not None:
                if current.id in seen:
                    raise ValueError("Folder hierarchy contains a cycle")
                seen.add(current.id)
                current = by_id.get(current.parent_id) if current.parent_id else None

    def to_bytes(self) -> bytes:
        self.validate()
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "FolderStore":
        data = json.loads(raw.decode("utf-8"))
        store = cls(schema=data.get("schema", SCHEMA_VERSION), folders=[Folder(**item) for item in data.get("folders", [])])
        store.validate()
        return store


@dataclass(slots=True)
class Entry:
    id: str
    title: str
    kind: str = "account"
    usernames: list[str] = field(default_factory=list)
    password: str | None = None
    totp: list[TotpConfig] = field(default_factory=list)
    actions: list[Action] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    notes: str = ""
    custom_fields: dict[str, str] = field(default_factory=dict)
    folder_id: str | None = None
    revision: int = 1
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    schema: int = SCHEMA_VERSION

    @classmethod
    def create(cls, title: str, **kwargs: Any) -> "Entry":
        return cls(id=str(uuid.uuid4()), title=title, **kwargs)

    def validate(self) -> None:
        if self.schema != SCHEMA_VERSION:
            raise ValueError(f"Unsupported entry schema: {self.schema}")
        uuid.UUID(self.id)
        if self.folder_id is not None:
            uuid.UUID(self.folder_id)
        if not self.title.strip():
            raise ValueError("Entry title is empty")
        if self.revision < 1:
            raise ValueError("Revision must be positive")
        for token in self.totp:
            token.validate()
        for action in self.actions:
            action.validate()

    def to_bytes(self) -> bytes:
        self.validate()
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "Entry":
        data = json.loads(raw.decode("utf-8"))
        data["totp"] = [TotpConfig(**item) for item in data.get("totp", [])]
        data["actions"] = [Action(**item) for item in data.get("actions", [])]
        data.setdefault("custom_fields", {})
        data.setdefault("folder_id", None)
        entry = cls(**data)
        entry.validate()
        return entry


@dataclass(slots=True)
class CatalogItem:
    id: str
    title: str
    kind: str
    usernames: list[str]
    tags: list[str]
    url_hosts: list[str]
    capabilities: list[str]
    revision: int
    ciphertext_sha256: str
    folder_id: str | None = None


@dataclass(slots=True)
class Catalog:
    items: list[CatalogItem] = field(default_factory=list)
    folders: list[Folder] = field(default_factory=list)
    schema: int = SCHEMA_VERSION

    def to_bytes(self) -> bytes:
        return json.dumps(asdict(self), ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")

    @classmethod
    def from_bytes(cls, raw: bytes) -> "Catalog":
        data = json.loads(raw.decode("utf-8"))
        if data.get("schema") != SCHEMA_VERSION:
            raise ValueError("Unsupported catalog schema")
        items = []
        for item in data.get("items", []):
            item.setdefault("folder_id", None)
            items.append(CatalogItem(**item))
        folders = [Folder(**item) for item in data.get("folders", [])]
        return cls(schema=data["schema"], items=items, folders=folders)
