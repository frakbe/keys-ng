from __future__ import annotations

from dataclasses import dataclass
import re
import uuid

from keys_ng.errors import ReferenceError

# KeePassXC-compatible UUID cross-reference subset used by Keys NG.
# We deliberately support UUID lookup only (@I) and the U/P target fields.
_REFERENCE_RE = re.compile(r"^\{REF:([UP])@I:([0-9A-Fa-f-]{32,36})\}$")


@dataclass(frozen=True, slots=True)
class EntryReference:
    field: str
    entry_id: str

    @property
    def field_name(self) -> str:
        return "username" if self.field == "U" else "password"


def normalize_entry_uuid(value: str) -> str:
    try:
        return str(uuid.UUID(value.strip()))
    except (ValueError, AttributeError) as exc:
        raise ReferenceError(f"Invalid referenced entry UUID: {value}") from exc


def parse_entry_reference(value: str | None) -> EntryReference | None:
    if value is None:
        return None
    match = _REFERENCE_RE.fullmatch(value.strip())
    if not match:
        return None
    field, raw_uuid = match.groups()
    return EntryReference(field=field, entry_id=normalize_entry_uuid(raw_uuid))


def make_entry_reference(field: str, entry_id: str, *, keepass_uuid: bool = False) -> str:
    field = field.upper().strip()
    if field not in {"U", "P"}:
        raise ReferenceError("Reference field must be U (username) or P (password)")
    normalized = normalize_entry_uuid(entry_id)
    rendered_uuid = uuid.UUID(normalized).hex.upper() if keepass_uuid else normalized
    return f"{{REF:{field}@I:{rendered_uuid}}}"
